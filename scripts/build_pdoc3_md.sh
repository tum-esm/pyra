#!/bin/bash

pdoc -o build/ packages/core --template-dir packages/docs/pdoc-config                     

if [ -d "packages/docs/docs/api-reference/core" ]; then
    rm -rf "packages/docs/docs/api-reference/core"
fi

mv build/core packages/docs/docs/api-reference/
rm -rf build/
