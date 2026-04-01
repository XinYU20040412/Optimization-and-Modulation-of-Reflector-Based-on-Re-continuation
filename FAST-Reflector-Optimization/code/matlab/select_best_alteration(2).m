function [delta_rs,best_RMSE,final_equation]=select_best_alteration(angles,R)
    Xs=R*sin(angles);Ys=-R*cos(angles);
    N = 1000;  %种群内个体数目
    N_chrom=size(angles,2)+1; %染色体节点数，也就是每个个体有多少条染色体，其实说白了就是看适应函数里有几个自变量。
    iter = 1000; %迭代次数，也就是一共有多少代
    mut = 0.2;  %突变概率
    acr = 0.2; %交叉概率
    chrom_range=[-0.6,0.6];%每个节点的值的区间
    fitness_ave = zeros(1, iter);%存放每一代的平均适应度
    fitness_best = zeros(1, iter);%存放每一代的最优适应度
    % 初始化，这只是用于生成第一代个体，并计算其适应度函数
    chrom = Initialize(N, N_chrom, chrom_range); %初始化染色体
    fitness = CalFitness(chrom,N,Xs,Ys,R); %计算适应度
    chrom_best = FindBest(chrom, fitness, N_chrom); %寻找最优染色体
    fitness_best(1) = chrom_best(end); %将当前最优存入矩阵当中
    fitness_ave(1) = CalAveFitness(fitness); %将当前平均适应度存入矩阵当中
    % 用于生成以下其余各代，一共迭代多少步就一共有多少代
    for t = 2:iter
        chrom = MutChrom(chrom, mut, N, N_chrom, chrom_range, t, iter); %变异
        chrom = AcrChrom(chrom, acr, N, N_chrom); %交叉
        fitness = CalFitness(chrom,N,Xs,Ys,R); %计算适应度
        chrom_best_temp = FindBest(chrom, fitness, N_chrom); %寻找最优染色体
        if chrom_best_temp(end)>chrom_best(end) %替换掉当前储存的最优
            chrom_best = chrom_best_temp;
        end
        %替换掉最劣
        [chrom, fitness] = ReplaceWorse(chrom, chrom_best, fitness);
        fitness_best(t) = -chrom_best(end); %将当前最优存入矩阵当中
        fitness_ave(t) = -CalAveFitness(fitness); %将当前平均适应度存入矩阵当中
    end
    delta_rs=chrom_best(1:end-1);
    best_RMSE=chrom_best(end);
    figure(1)
    plot(2:iter, fitness_ave(2:end), 'r', 2:iter, fitness_best(2:iter), 'b')
    ylabel('RMSE')
    xlabel('iteration')
    title('graph of genetic optimization ')
    grid on
    legend('average RMSE', 'min RMSE')
    disp(['最优染色体为', num2str(chrom_best(1:end-1))])
    disp(['最优适应度为', num2str(chrom_best(end))])
    Xs2=Xs+delta_rs(2:end).*(Xs./R);
    Ys2=Ys-delta_rs(2:end).*(Ys./R);
    final_equation=polyfit(Xs2,Ys2,4);
    disp(['最终曲线方程',num2str(final_equation)]);
end

function chrom_new = Initialize(N, N_chrom, chrom_range)
    chrom_new = rand(N, N_chrom);
    for i = 1:N_chrom %每一列乘上范围
        chrom_new(:, i) = chrom_new(:, i)*(chrom_range(2)-chrom_range(1))+chrom_range(1);
    end
end

function fitness = CalFitness(chrom,N,Xs,Ys,R)%计算适应度
    fitness = zeros(N, 1);
    for i = 1:N
        fitness(i) = CalRMSE(chrom(i,:),Xs,Ys,R);%%该函数是定义的适应度函数，也可称为代价函数，用于以后筛选个体的评价指标
    end
end

function chrom_new = MutChrom(chrom, mut, N, N_chrom, chrom_range, t, iter)%进行变异处理
    for i = 1:N %%N是个体总数，也就是每一代有多少头袋鼠
        for j = 1:N_chrom  %N_chrom是染色体节点数，就是有几条染色体
            mut_rand = rand; %随机生成一个数，代表自然里的基因突变，然后用改值来决定是否产生突变。
            if mut_rand <=mut  %mut代表突变概率，即产生突变的阈值，如果小于0.2的基因突变概率阈值才进行基因突变处理，否者不进行突变处理
                mut_pm = rand; %增加还是减少
                mut_num = rand*(1-t/iter)^2;
                if mut_pm<=0.5
                    chrom(i, j)= chrom(i, j)*(1-mut_num);
                else
                    chrom(i, j)= chrom(i, j)*(1+mut_num);
                end
                chrom(i, j) = IfOut(chrom(i, j), chrom_range); %检验是否越界
            end
        end
    end
    chrom_new = chrom;%%把变异处理完后的结果存在新矩阵里
end

function chrom_new = AcrChrom(chrom, acr, N, N_chrom)
    for i = 1:N
        acr_rand = rand;%生成一个代表该个体是否产生交叉的概率大小，用于判别是否进行交叉处理
        if acr_rand>acr %如果该个体的交叉概率值大于产生交叉处理的阈值，则对该个体的染色体（两条，因为此案例中有两个自变量）进行交叉处理
            acr_chrom = floor((N-1)*rand+1); %要交叉的染色体
            acr_node = floor((N_chrom-1)*rand+1); %要交叉的节点
            %交叉开始
            temp = chrom(i, acr_node);
            chrom(i, acr_node) = chrom(acr_chrom, acr_node); 
            chrom(acr_chrom, acr_node) = temp;
        end
    end
    chrom_new = chrom;
end

function chrom_best = FindBest(chrom, fitness, N_chrom)
    chrom_best = zeros(1, N_chrom+1);
    [maxNum, maxCorr] = max(fitness);%因为所有个体对应的适应度大小都被存放在fitness矩阵中
    chrom_best(1:N_chrom) =chrom(maxCorr, :);
    chrom_best(end) = maxNum;
end

function c_new = IfOut(c, range)
    if c<range(1) || c>range(2)
        if abs(c-range(1))<abs(c-range(2))
            c_new = range(1);
        else
            c_new = range(2);
        end
    else
        c_new = c;
    end
end


function [chrom_new, fitness_new] = ReplaceWorse(chrom, chrom_best, fitness)
    max_num = max(fitness);
    min_num = min(fitness);
    limit = (max_num-min_num)*0.2+min_num;
    replace_corr = fitness<limit;
    replace_num = sum(replace_corr);
    chrom(replace_corr, :) = ones(replace_num, 1)*chrom_best(1:end-1);
    fitness(replace_corr) = ones(replace_num, 1)*chrom_best(end);
    chrom_new = chrom;
    fitness_new = fitness;
end

function fitness_ave = CalAveFitness(fitness)
    [N ,~] = size(fitness);
    fitness_ave = sum(fitness)/N;
end

function RMSE=CalRMSE(delta_r,Xs,Ys,R)
    a=(1-0.466)*R;p=2*(R-a+delta_r(1));
    Xs2=Xs+delta_r(2:end).*(Xs./R);
    Ys2=Ys-delta_r(2:end).*(Ys./R);
    Ys_ideal=(Xs2.^2-p^2-2*a*p)/(2*p);
    RMSE=-sqrt(sum((Ys_ideal-Ys2).^2)/size(Ys,2));
end