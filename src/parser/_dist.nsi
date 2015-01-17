!include "MUI2.nsh"

!define PROGNAME "Uberparser"
!define PROGEXE "Uberparser.exe"
!define PROGVER "2.2"

!define PROGPATH "\${PROGNAME}"
OutFile "uberparser-${PROGVER}-inst.exe"
Name "${PROGNAME} ${PROGVER}"

WindowIcon on
Icon "uberparser.ico"

XPStyle on
SetCompressor /SOLID lzma
InstallDir $PROGRAMFILES${PROGPATH}
RequestExecutionLevel admin

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "uberparser.bmp"
!define MUI_ABORTWARNING

!define MUI_WELCOMEPAGE_TITLE "Добро пожаловать в установщик ${PROGNAME}"
!define MUI_WELCOMEPAGE_TEXT "По вопросам поддержки обращайтесь на наш форум: http://blap.ru/forum/"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\docs\License.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Russian"

Section ""
    SetOutPath $INSTDIR
    File /r /x *.db /x *.log /x *.cfg build\exe.win32-2.6\*.*
    CreateShortCut "$Desktop\${PROGNAME}.lnk" "$INSTDIR\${PROGEXE}" "" "$INSTDIR\${PROGEXE}" 0
    WriteRegStr HKLM SOFTWARE\Snoa\Uberparser2 "Installed" "Maybe"
SectionEnd
