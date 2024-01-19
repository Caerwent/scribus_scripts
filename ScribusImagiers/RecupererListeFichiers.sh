 #!/bin/bash
echo "TEXT1,text2,textFR,pic" > ImagierListeFichiers.csv
ls -1 ./img | while read x ; do echo ,,,$x ; done >> ImagierListeFichiers.csv
