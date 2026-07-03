# Script to tar figures actually used in the manuscript to make copying to my local laptop easier

figs=( CtrlSfcPtVerif.pdf                  
       CtrlUA0hVerif.pdf                    
       CtrlUA6hVerif.pdf                    
       DataImpactProduction.pdf             
       DataImpactSpinup.pdf                
       RMSDtimeseriesGFSspring.pdf          
       RMSEtimeseriesNRspring01.pdf
       RMSEtimeseriesRAOBspring01.pdf
       UASosseLowerAtmVerifPct00Spring.pdf
       UASosseLowerAtmVerifPct06Spring.pdf )

mkdir -p cp_figs
for f in ${figs[@]}; do
  cp ${f} ./cp_figs
done

tar cvf figs.tar ./cp_figs/*

rm -rf cp_figs
