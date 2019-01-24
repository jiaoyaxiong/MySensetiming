#!/bin/bash

#在当前目录下的raw_data文件夹下放置指定的文件夹下放置原始文件

keywords=$1


apidd=`ps -ef | grep SenseMediaAlgoService | grep -i ${keywords}| grep -v color |awk  {'print $2'}`
echo keywords is ${keywords} pid is ${apidd}



mkdir -p raw_data
file_name=raw_data

huitu(){
# kill backgroud pid
echo begin to kill background process 
kill -9 ${pid_neicun}
kill -9 ${pid_xiancun}
kill -9 ${pid_cpu}
kill -9 ${pid_gpu}




echo "
    set terminal pngcairo lw 2
    set title \"Memory change\"
    set ylabel \"memory free\"
    set output './${file_name}/memory.png'
    plot \"${file_name}/mem.txt\" using 1 w lp pt 7 title \"memory\"
    set output
    " | gnuplot


echo "
    set terminal pngcairo lw 2
    set title \"xiancun change\"
    set ylabel \"xiancun used\"
    set output './${file_name}/xiancun.png'
    plot \"${file_name}/xiancun.txt\" using 1 w lp pt 7 title \"xiancun\"
    set output
    " | gnuplot


echo "
    set terminal pngcairo lw 2
    set title \"cpu change\"
    set ylabel \"cpu idle\"
    set output './${file_name}/cpu_idle.png'
    plot \"${file_name}/cpu_idle.txt\" using 1 w lp pt 7 title \"cpu_idle\"
    set output
    " | gnuplot


echo "
    set terminal pngcairo lw 2
    set title \"gpu change\"
    set ylabel \"gpu used\"
    set output './${file_name}/gpu.png'
    plot \"${file_name}/GPU.txt\" using 1 w lp pt 7 title \"gpu\"
    set output
    " | gnuplot

}

#set terminal wxt

trap 'echo begin huitu!!!;huitu;exit'  2

mem_interval=1
xiancun_interval=1
cpu_interval=1
gpu_interval=1




#内存
TotalMem=`free -m|awk 'NR==2 {print $2}'`
echo TotalMem is ${TotalMem}
while true;do free -m|awk 'NR==2 {print $4}'>>${file_name}/mem.txt ;sleep ${mem_interval};done &
pid_neicun=`echo $!`
echo monitot neicun pid is ${pid_neicun}
#显存
Totalxiancun=`nvidia-smi |sed -n 9p |awk '{print $11}'`
echo TotalXIANCUN is ${Totalxiancun}
while true;do nvidia-smi |sed -n 9p |awk '{print $9}'|sed  s/MiB//g  >> ${file_name}/xiancun.txt ;sleep ${xiancun_interval};done &
pid_xiancun=`echo $!`
echo monitor xiancun pid is ${pid_xiancun}
#CPU利用率

while true;do top -p ${apidd} -b -n 1 | tail -n 1 | awk {'print $9'}>>${file_name}/cpu_idle.txt; sleep ${cpu_interval} ;done &
pid_cpu=`echo $!`
echo monitor cpu pid is ${pid_cpu}
#GPU利用率

while true;do nvidia-smi  | sed -n 9p | awk '{print $13}'>>${file_name}/GPU.txt;sleep ${gpu_interval} ;done &
pid_gpu=`echo $!`
echo monitor gpu pud is ${pid_gpu}


while true;do sleep 5;done
