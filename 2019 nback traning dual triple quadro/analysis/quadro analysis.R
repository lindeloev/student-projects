#############
# LOAD DATA #
#############

library(tidyverse)
library(BayesFactor)

# Read all data. Shorter phase names
D_all = readbulk::read_bulk('data') %>%
  mutate(
    score_avg = mean(c(color_score, position_score, sound_score, figure_score), na.rm = T),
    phase = factor(phase, levels=c('practice', 'pretest', 'training', 'posttest')),
    instruction = factor(instruction, labels=c('transfer', 'training')),
    task = as.character(task),
    task = recode(task, pc2 = 'PC2', fc2 = 'CS2', pcs1 = 'PAC1', fcs1 = 'ACS1', pcfs12 = 'PACS1'),
    task = factor(task, levels=c('ps2', 'PC2', 'CS2', 'PAC1', 'ACS1', 'PACS1', 'p1', 'f2', 'sc2', 'pcfs1')),
  )



###############################
# TEST-DATA: GAINS AND DPRIME #
###############################

# Compute d-prime measures (using psych::dprime) on the current df groupings.
add_dprime = function(df) {
  df = df %>%
    summarise(
      score = mean(score_avg),
      n_hit = sum(
        color_target & color_response,
        position_target & position_response,
        sound_target & sound_response,
        figure_target & figure_response,
        na.rm = T
      ),
      n_fa = sum(
        !color_target & color_response,
        !position_target & position_response,
        !sound_target & sound_response,
        !figure_target & figure_response,
        na.rm = T
      ),
      n_miss = sum(
        color_target & !color_response,
        position_target & !position_response,
        sound_target & !sound_response,
        figure_target & !figure_response,
        na.rm = T
      ),
      n_cr = sum(
        !color_target & !color_response,
        !position_target & !position_response,
        !sound_target & !sound_response,
        !figure_target & !figure_response,
        na.rm = T
      )
    )
  
  # Add computed SDT stuff
  cbind(df, psycho::dprime(df$n_hit, df$n_fa, df$n_miss, df$n_cr))
}


# Pretest-posttest
D_test = D_all %>%
  # Only pretest and posttest
  filter(phase %in% c('pretest', 'posttest')) %>%
  
  # Calculate SDT measures for each participant for each task and phase
  group_by(id, task, phase, instruction) %>%
  add_dprime()


# Identify data to be excluded
remove_these = D_test %>%
  group_by(task) %>%
  filter(phase == 'pretest', task %in% c('PC2', 'CS2')) %>%
  filter(dprime < 0.6) %>%
  select(id, task, instruction, dprime) %>%
  group_by(id) %>%
  tally() %>%
  filter(n == 2)

D_test = filter(D_test, !id %in% remove_these$id)




#############
# TEST DATA #
#############

# Plot
ggplot(D_test, aes(x=instruction, y=dprime, fill=phase)) +
  #stat_summary(fun.y = mean, geom='bar', position='dodge') + 
  #stat_summary(fun.data = mean_cl_boot, geom='errorbar', position=dodge, width=0.2, color='#555555') + 
  tidybayes::stat_interval(position=position_dodge(width=0.6)) +  # Dodge does not work
  facet_grid(~task) + 
  scale_fill_manual(values=c('black', 'gray')) +
  
  ggthemes::theme_wsj(13) + 
  labs(title='Test scores', x='instruction', y='dprime') + 
  theme(
    axis.title = element_text(size = rel(0.5)),
    axis.text.x = element_text(angle=90),
    legend.position = c(0.1, 0.8),
    legend.direction='vertical',
    legend.title = element_text(size = rel(0.5)),
    legend.background = element_blank()
  )


# Is there differential improvement between tasks? 
X1 = lmBF(dprime ~ task * phase * instruction, D_test, whichRandom='id')
X2 = lmBF(dprime ~ task * phase * instruction - task:phase:instruction, D_test, whichRandom='id')
X1 / X2  # BF
summary(posterior(X1, iterations = 1000))  # Estimates

# Is there an overall improvement from baseline to post?
X1 = lmBF(dprime ~ phase*instruction + task, D_test, whichRandom='id')
X2 = lmBF(dprime ~ phase + instruction + task, D_test, whichRandom='id')
X1 / X2  # BF
summary(posterior(X1, iterations = 1000))  # Estimates




#################
# TRAINING DATA #
#################

# Bin the training and compute d-prime measures
N_BINS = 5  # Number of bins.
D_train = filter(D_all, phase == 'training') %>%
  group_by(id) %>%
  mutate(trial_global = row_number(),
         time_bin = as.numeric(cut(trial_global, N_BINS))) %>%
  group_by(id, instruction, time_bin) %>%
  add_dprime2()

# Training improvement
D_train_change = D_train %>% 
  filter(time_bin %in% c(1,5)) %>% 
  mutate(change = dprime - lag(dprime, 1)) %>% 
  select(id, time_bin, dprime, change) %>% 
  filter(time_bin == 5)

x = ttestBF(D_train_change$change, D_train_change$instruction)
q = posterior(x, iterations=1000)

ggplot(D_train_change, aes(x = id, y = change)) +
  geom_bar() + 
  facet_wrap(~instruction)


# Plot training data
ggplot(D_train, aes(x = time_bin, y = dprime, group = id)) +
  geom_line() +
  #stat_smooth(method=lm, se = FALSE) +
  stat_smooth(
    aes(group = 1),
    #method = lm,
    color = 'red',
    lwd = 3
  ) +
  facet_grid(~ instruction) +
  labs(title = 'Training effects', x = 'Bin of 50 trials', y = 'dprime') +
  ggthemes::theme_wsj(13) + 
  theme(
    axis.title = element_text(size = rel(0.5))
  )


# Model comparison
X1 = lmBF(dprime ~ time_bin * instruction, D_train, whichRandom='id')
X2 = lmBF(dprime ~ time_bin + instruction, D_train, whichRandom='id')
X1 / X2  # BF
summary(posterior(X2, iterations = 1000))  # Estimates






#################################################
# SAVE IN SPSS/JASP/Jamovi FRIENDLY WIDE FORMAT #
#################################################

# D_semiwide = D_test %>%
#   # Now make one column for each of these values for pretest and posttest
#   # Thanks to https://community.rstudio.com/t/spread-with-multiple-value-columns/5378/5 for this approach
#   ungroup() %>%
#   mutate(phase = recode_factor(phase, pretest = 'pre', posttest = 'post')) %>%  # shorter column names
#   nest(score,
#        dprime,
#        n_hit,
#        n_fa,
#        n_miss,
#        n_cr,
#        beta,
#        aprime,
#        bppd,
#        c,
#        .key = 'value_col') %>%
#   spread(key = phase, value = value_col) %>%
#   unnest(pre, post, .sep = '_') %>%
#   
#   # Compute difference
#   mutate(score = post_score - pre_score,
#          dprime = post_dprime - pre_dprime)
# 
# write.csv(D_semiwide, 'test_results.csv', row.names = FALSE)
# 
# # Change 'dprime' below to 'score' if you want to analyze that
# D_wide = D_test %>%
#   select(id, task, instruction, dprime) %>%
#   spread(task, dprime)
# write.csv(D_wide, 'dprime_wide.csv')



# dodge <- position_dodge(width = 0.9)
# ggplot(D_semiwide, aes(x=task, y=dprime, fill=instruction)) + 
#   #tidybayes::stat_interval(position=position_dodge(width=0.5)) + 
#   #stat_summary(fun.y = mean, geom='bar', position=dodge) + 
#   #stat_summary(fun.data = mean_cl_boot, geom='errorbar', position=dodge, width=0.2, color='#555555') + 
#   tidybayes::stat_interval(position=position_dodge(width=0.6)) +  # Dodge does not work
#   scale_fill_manual(values=c('black', 'gray')) +
#   ggthemes::theme_wsj(13) + 
#   labs(title='Transfer effects', x='Task on transfer spectrum', y='dprime improvement') + 
#   theme(
#     axis.title = element_text(size = rel(0.5)),
#     axis.text.x = element_text(angle=90),
#     legend.position = c(0.8, 0.85),
#     legend.direction='vertical',
#     legend.background = element_blank(),
#     legend.title = element_text(size = rel(0.5))
#   )



####################
# BAYESIAN VERSION #
####################
# Advantage: uses single-trial data for greater propagation of uncertainty.
# NOT FINISHED. Criterion values look off. dprime values are good.
# Inspired by this tutorial: 
# https://vuorre.netlify.com/post/2017/10/12/bayesian-estimation-of-signal-detection-theory-models-part-2/
# 
# 
# Make one trial into four trials as if the participant responded to each stimulus
# in each trial. Needed to do univariate regression, but it is probably not
# completely inferentially accurate.
# D = D_all %>%
#   filter(phase %in% c('pretest', 'posttest')) %>%
#   pivot_longer(c('color_target', 'position_target', 'sound_target', 'figure_target'), names_to = 'target_stim', values_to = 'target') %>%
#   pivot_longer(c('color_response', 'position_response', 'sound_response', 'figure_response'), 'resp', names_to = 'response_stim', values_to = 'response') %>%
#   mutate(target_stim = str_replace(target_stim, '_target', ''),
#          response_stim = str_replace(response_stim, '_response', '')) %>%
#   filter(target_stim == response_stim, !is.na(target))
# 
# 
# library(brms)
# model_all = response ~ target * phase * task * instruction + (1 | id)
# fit2 = brm(model_all, D, family=bernoulli(link='probit'))

