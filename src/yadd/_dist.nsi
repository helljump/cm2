!include "MUI2.nsh"

!define PROGNAME "Yadd"
!define PROGEXE "yadd.exe"
!define PROGVER "1.1"

!define PROGPATH "\${PROGNAME}"
OutFile "yadd-${PROGVER}-inst.exe"
Name "${PROGNAME} ${PROGVER}"

WindowIcon on
Icon "yadd.ico"

XPStyle on
SetCompressor /SOLID lzma
InstallDir $PROGRAMFILES${PROGPATH}
RequestExecutionLevel user

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "yadd.bmp"
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
    File /r /x *.db /x *.log /x *.cfg build\release\*.*
    CreateShortCut "$Desktop\${PROGNAME}.lnk" "$INSTDIR\${PROGEXE}" "" "$INSTDIR\${PROGEXE}" 0
SectionEnd
