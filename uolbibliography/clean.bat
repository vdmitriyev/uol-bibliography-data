@echo off
REM @author Viktor Dmitriyev
REM @about Remove '__temp__' and "generated" folders
rmdir /s /q __temp__
rmdir /s /q generated
rmdir /s /q logs