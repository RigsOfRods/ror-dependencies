DirectX9 deps for RoR
=====================

RoR uses OGRE 1.9 which requires 'Microsoft DirectX SDK (June 2010)' installed.
However, this SDK has known installation issues and may break dev environment
in more than one way. Furthermore, all DirectX versions up to 11 are officially
obsoleted by Microsoft, the functionality is now part of Windows SDK.

Reading:
https://blogs.msdn.microsoft.com/chuckw/2011/12/09/known-issue-directx-sdk-june-2010-setup-and-the-s1023-error/
https://blogs.msdn.microsoft.com/chuckw/2013/08/20/living-without-d3dx/
https://blogs.msdn.microsoft.com/chuckw/2015/08/05/where-is-the-directx-sdk-2015-edition/
https://blogs.msdn.microsoft.com/chuckw/2015/03/23/the-zombie-directx-sdk/

This package contains Dx9 headers/binaries not included in Windows SDK, as
detailed in the "Zombie DirectX SDK" article.

The subdirectory 'License Agreements' is copied verbatim from the SDK.
Please see the included documents for more details.

