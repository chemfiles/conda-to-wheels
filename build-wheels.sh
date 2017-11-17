
tar -C chemfiles --strip-components 1 -xf build/${CHEMFILES_LIB} "lib/lib*"

cat > chemfiles/location.py << EOF
import os

dirname = os.path.dirname(__file__)
CHEMFILES_LOCATION = os.path.join(dirname, "libchemfiles.dylib")
EOF

python setup.py bdist_wheel --plat-name macosx-10.9-x86_64
