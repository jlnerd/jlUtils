"""
Build the repo's docs/build/html folder from which sphinx docs will be hosted

If unexpected warnings occur during the build, the script will fail
so that the user can address the warnings.
"""

#Import libs
import sys, os, shutil
import subprocess

API = 'fuegodata'

### Helper Functions ####
def bash_command(command):
    """
    Executes a terminal/bash/CLI command passed as a string and returns the outputs or raises an error if the command fails
    
    Args:
        command: string. The command to be executed
        
    Returns:
        output: string. The CLI/terminal/bash output
    """

    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        raise (BaseException(e.output.decode("utf-8")))

    return output

def copy_README_to_source():
    """
    Copy the root README file into the source file
    to ensure the README of the docs is up to date
    (github pages will get annoyed at symbolick links)
    """
    destination = 'docs/source/README.md'
    
    if os.path.isfile(destination):
        os.remove(destination)
    shutil.copy('README.md',destination)

def combine_Subpackages_and_Submodules_in_API(API):
    """
    Load the {API}.rst file created by sphinx-apidoc and
    combine the `Submodules` and `Subpackages` sections together
    for improved readability
    
    Args:
        API: string. the name of the API for which the docs
           are being created
    """
    file = f'docs/source/{API}.rst'
    with open(file, 'r') as f:
        text = f.read()

    lines = text.split('\n')

    new_submodule_lines = []
    Subpackages_found = False
    Submodules_found = False
    for line in lines.copy():
        if 'Subpackages' in line:
            Subpackages_found = True
            Submodules_found = False
        elif 'Submodules' in line:
            Subpackages_found = False
            Submodules_found = True
        elif 'Module contents' in line:
            break
            
        if Subpackages_found:
            if API in line:
                new_submodule_lines.append(line)
            lines.remove(line) #Remove all lines associated with `Subpackages` sections
            
        if Submodules_found and API in line:
            new_submodule_lines.append(line)
            lines.remove(line)
            
    new_submodule_lines = list(reversed(sorted(new_submodule_lines)))
    
    for i, line in enumerate(lines.copy()):
        if 'Submodules' in line:
            Submodules_found = True
        if Submodules_found:
            if 'maxdepth' in line:
                i+=2
                break
    for new_line in new_submodule_lines:
        lines.insert(i, new_line)

        
    #print('\n'.join(lines))
    with open(file, 'w') as f:
        f.write('\n'.join(lines))
        
def place_Module_contents_first(API):
    """
    Load all the {API}*.rst files and make sure the
    `Module contents` sections is the first section on
    the page
    
    Args:
        API: string. the name of the API for which the docs
           are being created
    
    """
    source_dir = 'docs/source/'
    files = os.listdir(source_dir)
    module_files = [f for f in files if API in f]
    
    for file in module_files:
        
        fpath = os.path.join(source_dir,file)
        
        with open(fpath, 'r') as f:
            text = f.read()
            lines = text.split('\n')
            
        Module_contents_found = False
        Module_contents_lines = []
        for line in lines.copy():
            if line == 'Module contents' :
                Module_contents_found = True
            if Module_contents_found:
                lines.remove(line)
                Module_contents_lines.append(line)
        
        for line in reversed(Module_contents_lines):
            lines.insert(2, line)
            
        if len(Module_contents_lines)>0:
            lines.insert(2, '')
                
        with open(fpath, 'w') as f:
            f.write('\n'.join(lines))
    
        
def convert_package_headers_to_module_headers(API):
    """
    Load the all the {API}.module.rst files and make sure the
    header is of form  ""{API}.module module"
    
    Args:
        API: string. the name of the API for which the docs
           are being created
    """
    source_dir = 'docs/source/'
    files = os.listdir(source_dir)
    module_files = [f for f in files if API in f and f != f'{API}.rst']
    for file in module_files:
        
        fpath = os.path.join(source_dir,file)
        
        with open(fpath, 'r') as f:
            text = f.read()
            lines = text.split('\n')
            
        
        lines[0] = lines[0].replace('package', 'module')
        
        if len(lines)>=4:
            if 'Module contents' in lines[3]:
                lines.pop(3)
                lines.pop(3)
                lines.pop(3)
            
        with open(fpath, 'w') as f:
            f.write('\n'.join(lines))
            
def Add_markdown_files_to_index(API):    
    """
    Add all the markdown files contained in the `docs/source`
    directory as `toctree`s in the index.rst file
    
    Args:
        API: string. the name of the API for which the docs
           are being created
    """
    
    source_dir = 'docs/source/'
    files = os.listdir(source_dir)
    markdown_files = [f for f in files if '.md' in f and 'README' not in f]
    
    index_fpath = os.path.join(source_dir,'index.rst')
    with open(index_fpath, 'r') as f:
        text = f.read()
        
    toctree_text = '.. toctree::'
    toctree_split = text.split(toctree_text)
        
    toctree_template = '\n'.join(
        ['\n'
        '\t:maxdepth: 2',
        '\t:caption: CAPTION_TEXT',
         '',
        '\tMARKDOWN_FILENAME',
         '',
         ''
        ]
    )
    
    #Add new markdown files
    for file in markdown_files:
        
        MARKDOWN_FILENAME = file.replace('.md','')
        CAPTION_TEXT = MARKDOWN_FILENAME.replace('_',' ').split(' ')
        CAPTION_TEXT = ' '.join([t.capitalize() for t in CAPTION_TEXT])
        
        new_toctree = toctree_template.replace('MARKDOWN_FILENAME', MARKDOWN_FILENAME)
        new_toctree = new_toctree.replace('CAPTION_TEXT', CAPTION_TEXT)
        
        if MARKDOWN_FILENAME not in text:
        
            toctree_split.insert(-1, new_toctree)
            
    #Make sure none-existing markdown files aren't present
    for split in toctree_split:
        if 'README' not in split and API not in split:
            valid_toctree=False
            for file in markdown_files:
                MARKDOWN_FILENAME = file.replace('.md','')
                if MARKDOWN_FILENAME in split:
                    valid_toctree=True
                    break
            if valid_toctree == False:
                toctree_split.remove(split)
        
    text = toctree_text.join(toctree_split)
    
    with open(index_fpath, 'w') as f:
        f.write(text)
        
def delete_unnecessary_files():
    """
    Delete files that aren't critical to github/sphinx page docs
    """
    files = ['docs/build/doctrees/environment.pickle']
    
    for file in files:
        os.remove(file)
        
        
    
### End of Helper Functions ####


#Instal requirements for sphinx
command = ';'.join(['cd docs/','pip install -q -r requirements.txt'])
output = bash_command(command)
print(output)

#Reconstruct the API docs
command = ';'.join([f"sphinx-apidoc -f -e -a -o docs/source/ {API}/"])
output = bash_command(command)
print(output)

copy_README_to_source()

#Cleanup the automatically generated docs from sphinx-apidoc
combine_Subpackages_and_Submodules_in_API(API)
convert_package_headers_to_module_headers(API)
place_Module_contents_first(API)
Add_markdown_files_to_index(API)

#Cleanup the build dir
command = ';'.join(['cd docs/', 'make clean'])
output = bash_command(command)
print(output)

#Make/Build the html dir
make_html_dir = ';'.join(['cd docs/',
                          'make html'])
output = bash_command(make_html_dir)

filtered_output = []
for line in output.split('\n'):
    if 'WARNING' not in line:
        filtered_output.append(line)
    else:
        prefix = line.split('WARNING:')[0]
        suffix = line.split('WARNING:')[1]
        splits = suffix.split(';')
        filtered_splits = []
        
        for split in splits:
            valid_warning = True
            for ignored_warning in ['Definition list ends without a blank line',
                                    'unexpected unindent',
                                    'duplicate label',
                                    'duplicate object description',
                                    'Unexpected indentation',
                                    'None:any reference target not found'
                                   ]:
                if ignored_warning in split:
                    valid_warning = False
                    break
            if valid_warning:
                filtered_splits.append(split)
        
        if len(filtered_splits) > 0:
            #append to filtered output if all warnings weren't dropped
            
            line = prefix + 'WARNING:' + ';'.join(filtered_splits)
            
            filtered_output.append(line)
filtered_output = '\n'.join(filtered_output)
print(filtered_output)

assert 'WARNING' not in filtered_output, f'The "{make_html_dir}" command returned unacceptable WARNING(s). Please address, then try again.'

delete_unnecessary_files()

# make latexpdf

# echo ""
# echo "-------------- make linkcheck --------------"
# make linkcheck

print('!!build docs complete!!')