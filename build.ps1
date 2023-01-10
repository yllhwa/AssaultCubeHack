python setup.py build_ext --inplace
pyinstaller main.spec
rm -r -fo build
rm packages/*.c
rm *.pyd