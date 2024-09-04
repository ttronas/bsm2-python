# BSM2-Python Documentation

## Documentation setup on local machines

If you want to improve the documentation of this project on your local machine, there are a few setup-steps before you can begin.
In order to use [mkdocs] you have to:

 1. Install the [GTK-Package]: 
 
    - Download and install [MSYS2].

    - Start the MSYS2-Shell

    - Install the GTK4-Package:

    ```console
    pacman -S mingw-w64-x86_64-gtk4
    ``` 
    
    - Install the compiler for Python:
 
    ```console
    pacman -S mingw-w64-x86_64-python-gobject
    ```

 2. Add the MSYS2 path to the Environment Variables:

    - Add the path `C:\msys64\mingw64\bin` to your Environment Variables.

    - To do this, go to the Control Panel and open "System and Security" > "System" > "Advanced System Settings".

    - Click on "Environment Variables" and edit the `PATH` variable by adding the path `C:\msys64\mingw64\bin`.

[GTK-Package]: https://www.gtk.org/docs/installations/windows/
[mkdocs]: https://www.mkdocs.org/
[MSYS2]: https://www.msys2.org/
