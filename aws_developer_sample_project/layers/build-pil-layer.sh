finch run -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.12" /bin/sh -c "pip install -r pil-layer-requirements.txt -t python/; exit"
zip pil-layer-python.zip -r python
rm -rf python
