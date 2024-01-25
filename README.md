# SPC-Core 
Sunfounder Power Control Core
aa
## Development

active virtual environment
```bash
# active virtual environment
source /opt/spc/venv/bin/activate

# build spc package
python3 -m build
# install spc package
pip3 install dist/spc-0.0.1-py3-none-any.whl --force-reinstall
# cleanup
rm -rf dist/ build/ spc.egg-info/

# Copy spc_server.py to /opt/spc/bin
cp ~/spc/bin/spc_server /opt/spc/spc_server
```

## Structure
- Service
  - bash script: run script, setup config, start service
    - venv
      - Python Package
        - Python Scripts

## About SunFounder
SunFounder is a company focused on STEAM education with products like open source robots, development boards, STEAM kit, modules, tools and other smart devices distributed globally. In SunFounder, we strive to help elementary and middle school students as well as hobbyists, through STEAM education, strengthen their hands-on practices and problem-solving abilities. In this way, we hope to disseminate knowledge and provide skill training in a full-of-joy way, thus fostering your interest in programming and making, and exposing you to a fascinating world of science and engineering. To embrace the future of artificial intelligence, it is urgent and meaningful to learn abundant STEAM knowledge.

## Contact us
website:
    www.sunfounder.com

E-mail:
    service@sunfounder.com