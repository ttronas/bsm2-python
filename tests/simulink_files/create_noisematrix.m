% simple script to expand the noise file to full 609 days

%load sensornoise_bsm2.mat
%save sensornoise_org_bsm2 SENSORNOISE

SENSORNOISEFULL = SENSORNOISE(1:(end-1),:);
[m,n] = size(SENSORNOISE);
m = m-1;
timevector = SENSORNOISE(1:(end-1),1);

for i = 1:43
    SENSORNOISEFULL = [SENSORNOISEFULL; SENSORNOISE(1:(end-1),:)];
    SENSORNOISEFULL((i*m)+1:end,1) = (i*14)+timevector;
end

SENSORNOISEFULL = SENSORNOISEFULL(1:(609*24*60+1),:);

save sensornoise_bsm2 SENSORNOISEFULL
