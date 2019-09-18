library(tidyverse)
D_meta = read.csv('D:/drive/Documents/projects/X STUDENT PROJECTS/2018-2019 subjective-objective/meta data.csv') %>%
  mutate(
    change_scale = t2_scale - t1_scale,
    change_index = change_scale * 5 + runif(n(), -2, 2),
    test = 'Healthy: Digit Span'
  ) %>%
  rename(obj_change = change_index, perceived = change_subj)




#cor.test(D$scale_change, D$change_subj)
cor.test(D_meta$change_raw, D_meta$change_subj)

ggplot(D_meta, aes(x=change_index, y=change_subj)) + 
  geom_jitter() + 
  geom_smooth(method='lm') +
  labs(x='Objective change', y = 'Reported change', title='Healthy change') + 
  theme_gray(15)
ggsave('figures/healthy change.png', width=3, height=3, dpi=300)
