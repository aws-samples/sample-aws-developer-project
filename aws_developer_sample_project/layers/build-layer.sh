finch run -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.12" /bin/sh -c "pip install -r $1-layer-requirements.txt -t python/; exit"
zip "$1-layer-python.zip" -r python
rm -rf python
