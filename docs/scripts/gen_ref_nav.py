"""Generate the code reference pages and navigation.

Copyright (c) 2019, Timothée Mazzucotelli, ISC License

Taken from https://github.com/mkdocstrings/mkdocstrings/blob/master/docs/gen_ref_nav.py
"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path('src').rglob('*.py')):
    module_path = path.relative_to('src').with_suffix('')
    doc_path = path.relative_to('src').with_suffix('.md')
    full_doc_path = Path('reference', doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == '__init__':
        parts = parts[:-1]
        doc_path = doc_path.with_name('index.md')
        full_doc_path = full_doc_path.with_name('index.md')
    elif parts[-1] == '__main__':
        continue
    elif parts[-1] == '_version':
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
        ident = '.'.join(parts)
        fd.write(f'::: {ident}')
        
        # Changes local mkdocstring options for folder files
        folder_names = ["bsm2_python", "bsm2_python.bsm2", "bsm2_python.bsm2.init", "bsm2_python.energy_management", "bsm2_python.energy_management.init", "bsm2_python.gases"]
        for folder in folder_names: 
            if folder == ident:
                fd.write("""
                    options:
                        show_symbol_type_heading: false
                        show_root_full_path: true
                        filters: [__all__]""")
                
        # Changes local mkdocstring options for init files
        # init_folder_names = ["bsm2_python.bsm2.init", "bsm2_python.energy_management.init"]
        # for init_folder in init_folder_names:
        #     if init_folder == ident:
        #         # fd.write("""
        #         #     \tshow_root_full_path""")
        #         break 
        #     elif "init" in ident and ident not in init_folder_names:
        #         fd.write("""
        #             options:
        #                 show_if_no_docstring: true""")
        #         break

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as nav_file:
    nav_file.writelines(nav.build_literate_nav())
