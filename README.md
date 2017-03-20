# ror-dependencies
Dependencies that will be needed to compile the source.

|  Build status 	|                                                                                                                                                                                     	|
|---------------	|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| Linux:        	| TODO                                                                                                                                                                                	|
| Windows:      	| [![appveyor build Status](https://img.shields.io/appveyor/ci/AnotherFoxGuy/ror-dependencies.svg?style=flat-square)](https://ci.appveyor.com/project/AnotherFoxGuy/ror-dependencies) 	|

## How to build on Windows

### Prerequisites

  * Install Windows Visual Studio 2015 Community Edition
  * Install [cmake](https://cmake.org/download/)
  * Install [git](https://git-scm.com/download) and [mercurial](https://www.mercurial-scm.org/)

Install with [Chocolatey](https://chocolatey.org/): ```choco install cmake git hg```

### Create Visual Studio solution file

  * Launch cmake-gui and point the source directory to the _ror-dependencies_ repository
  * Set the build directory to any folder where the resulting dependencies should be placed
  * Press _Configure_ and select `Visual Studio 14 2015` as generator (Notice: Win64 target not supported yet)
  * Press _Generate_ to create the solution file
  
### Build dependencies

  * Open the `ror-dependencies.sln` file inside the chosen build directory with Visual Studio
  * Select `Release` configuration (currently the only tested configuration)
  * Run Build->Build Solution (`Ctrl-Shift-B`)
  * This will populate the `Dependencies_Windows_Visual-Studio-14-2015` directory with the freshly built dependencies

## How to build on Linux

### Prerequisites

  * Install cmake, git and mercurial
  * Install WxWidgets
  
### Configure && build

    cmake <Path-to-ror-dependencies-repository>
	make
	
The resulting dependencies will be placed inside the `Dependencies_Linux` directory.
  
## Known issues

  * WxWidgets is not built from source; instead pre-built binaries are downloaded (might require VS2015 runtime for distributing)
  
