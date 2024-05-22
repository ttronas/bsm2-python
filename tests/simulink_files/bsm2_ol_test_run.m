init_bsm2;
% load ./Influent_data//stabilizeinfluent_bsm2.mat;
% sim("bsm2_ss_test");
tic
sim("bsm2_ol_test.slx");
time_elapsed = toc;
writematrix(effluent, 'bsm2_ol_eff_matlab.csv');
writematrix(time_elapsed, 'bsm2_ol_time_elapsed.csv');