
#把当前目录下的raw_data 所有文件上传到ftp 上面
#!/bin/bash
wenjianjia=raw_data
if [ -z ${wenjianjia} ];
then
   echo need a para
    exit 1

fi

filenames=$(ls ${wenjianjia})
echo ${filenames}
#OLD_IFS="$IFS"
#IFS=" "
#arr=($filenames)
#IFS="$OLD_IFS"
for s in ${filenames}
do
echo $s
ftp -n<<!
open 172.20.20.225
user sensemedia S@nsemedia2019
binary

cd /performance_data
mkdir $s
close
bye
!
done


for s in ${filenames}
do
for y in $(ls raw_data/$s)
do
echo $y
ftp -n<<!
open 172.20.20.225
user sensemedia S@nsemedia2019
binary

cd /performance_data/$s
lcd raw_data/$s
put $y
close
bye
!
done
done


