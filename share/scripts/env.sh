
export PATH="/bin/:$PATH"

export PS1='$(EXC=$?;if [ $EXC != 0 ] ;then echo \[\e[31m\]ERR "$EXC : " ; fi)\[\e]0;\w\a\]\[\e[32m\]\u@\H(\D{%Y-%m-%d} \t) \[\e[33m\]\w\[\e[0m\]$(GT=$(git branch 2>/dev/null|grep "*"); if [ -n "$GT" ];then echo -e -n "\E[3m [${GT#* }] \E[23m "; fi) \n\$ \[\e]2;\H \w\a\]'

if (type vim >/dev/null 2>&1);then alias vi="vim -c 'set bg=dark' -c 'syntax enable'"; fi
export EDITOR=vi
alias l="ls -la"; alias ll="ls -l" ; alias lf="ls -Fa"; alias sl="ls"; alias lt="ls -latr";
export PYTHONDONTWRITEBYTECODE="yes"

