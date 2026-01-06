#! /usr/bin/env bash

set -e
set -x

cd back
python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mv openapi.json front/
cd front
npm run generate-client
