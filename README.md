# Include fixer (c/c++)
Python script to fix the #include entries to makes them explicit (include paths)

Following google standard of the form: </br>
* #include "base/logging.h" </br>

[All of a project's header files should be listed as descendants of the project's source directory without use of UNIX directory aliases](https://google.github.io/styleguide/cppguide.html#Names_and_Order_of_Includes)

Additionally provides feedback if the #include has more than one possible entry for the user to take corective actions.

## How to run:

 python .\include-fixer.py -s \"C:\\library-xxxx\\source\" -i \"C:\\library-xxxx\\external-references;C:\\library-yyyy\include\" -o \"C:\\fixed-include\output\"
