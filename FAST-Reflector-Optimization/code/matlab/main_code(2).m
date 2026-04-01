clear;clc;
loc_table=readtable('附件1.csv');
var_names={'node','x','y','z'};
loc_table.Properties.VariableNames = var_names;
aim_name={'x','y','z'};
loc_mat=table2array(loc_table(:,aim_name));
loc_mat=loc_mat(:,1:3);
R=mean(sqrt((loc_mat(:,1).^2+loc_mat(:,2).^2+loc_mat(:,3).^2)));
N_chorm=100;angles=linspace(0,pi/6,N_chorm);
[delta_rs,best_RMSE,final_equation]=select_best_alteration(angles,R);
angles2=linspace(min(angles),max(angles),100);
delta_rs2=spline(angles,delta_rs(2:end),angles2);
delta_r_p=polyfit(angles2,delta_rs2,4);
a=36.7595/180*pi;b=pi/2-78.169/180*pi;
tran_mat=[cos(b),0,sin(b);0,1,0;-sin(b),0,cos(b)]*...
    [cos(a),-sin(a),0;sin(a),cos(a),0;0,0,1];
for i=1:size(loc_mat,1)
    loc_mat2(i,:)=(tran_mat\loc_mat(i,:)')'; %#ok<SAGROW>
end
logical_arr=(sqrt(loc_mat2(:,1).^2+loc_mat2(:,2).^2)<=150);
nodes=loc_table(logical_arr,'node');
nodes=table2cell(nodes);
loc_working_mat=loc_mat(logical_arr,:);
theta=asin(sqrt(loc_working_mat(:,1).^2+loc_working_mat(:,2).^2)/R);
flex_length=polyval(delta_r_p,theta);
loc_working_mat2(:,1)=loc_working_mat(:,1)+flex_length.*sin(theta)...
    .*(loc_working_mat(:,1)./(sqrt(loc_working_mat(:,1).^2+loc_working_mat(:,2).^2)));
loc_working_mat2(:,2)=loc_working_mat(:,2)+flex_length.*sin(theta)...
    .*(loc_working_mat(:,2)./(sqrt(loc_working_mat(:,2).^2+loc_working_mat(:,2).^2)));
loc_working_mat2(:,3)=loc_working_mat(:,3)-flex_length.*cos(theta);
for i=1:size(loc_working_mat2,1)
    loc_working_mat2(i,:)=(tran_mat*loc_mat(i,:)')';
end
filename='附件4.xlsx';start_row=2;
loc_working_cell=num2cell(loc_working_mat2);
loc_working_cell_entire=nodes;
for i=1:3
    loc_working_cell_entire=[loc_working_cell_entire,loc_working_cell(:,i)]; %#ok<AGROW>
end
flex_length=num2cell(flex_length);
flex_cell=[nodes,flex_length];
peak_coordinate=(tran_mat*[0;0;-(300+delta_rs(1))])';
peak_coordinate=num2cell(peak_coordinate);
writecell(loc_working_cell_entire,filename,'Sheet','调整后主索节点编号及坐标','Range',['A' num2str(start_row)]);%
writecell(flex_cell,filename,'Sheet','促动器顶端伸缩量','Range',['A' num2str(start_row)]);%
writecell(peak_coordinate,filename,'Sheet','理想抛物面顶点坐标','Range',['A' num2str(start_row)]);%
