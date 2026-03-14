
df<-read_csv("data/clean/census_clean.csv")
cpi_data<-read_csv("data/clean/tw_cpi.csv") %>%
  filter(year %in% c(1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021))

df<-df %>%
  left_join(cpi_data, by = "year") %>%
  mutate(
    real_compensation= labor_compensation / cpi_index * 100/1000,#/1000 is for formating
    real_labor_productivity  = labor_productivity / cpi_index * 100,
    real_capital_labor_ratio=capital_labor_ratio / cpi_index * 100,
    labour_share_gva = (labor_compensation * employees) / (value_added * 10000)
    )


df_early<-df %>% filter(year<=1996)
df_late<-df%>% filter(year>=2001)
# question 1: does productivity increase effect on wage increase?
model1<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df)
model1_early<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df_early)
model1_late<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df_late)

model1_weighted<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df,weights = employees)
model1_weighted_early<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df_early,weights = employees)
model1_weighted_late<-lm(log(real_compensation) ~ log(real_labor_productivity),data=df_late,weights = employees)


#proof the break point at 2001 exists
library(strucchange)

chow<-sctest(log(real_compensation) ~ log(real_labor_productivity),
       type = "Chow",
       point = which(unique(sort(df$year)) == 2001),
       data = df %>% arrange(year))


#question2 where does the productivity go?
model2 <- lm(log(real_labor_productivity) ~ log(real_capital_labor_ratio),
             data = df)
model2_weight <- lm(log(real_labor_productivity) ~ log(real_capital_labor_ratio),
             data = df,weights = employees)

model2_early <- lm(log(real_labor_productivity) ~ log(real_capital_labor_ratio),
             data = df_early)
model2_late <- lm(log(real_labor_productivity) ~ log(real_capital_labor_ratio),
             data = df_late)

model_share <- lm(labor_cost_ratio ~ log(real_labor_productivity),
                  data = df)

model_profit <- lm(profit_rate ~ log(real_labor_productivity),w=employees,
                   data = df)

#question 3: in terms of different industry

df <- df %>%
  mutate(sector = case_when(
    industry_code == "C" ~ "Manufacturing",
    industry_code %in% c("G","H","I","J","K","L","M","N","P","Q","R","S") ~ "Services",
    TRUE ~ "Other"
  ))

model3_mfg <- lm(log(real_compensation) ~ log(real_labor_productivity),
                 data = df %>% filter(sector == "Manufacturing"),
                 weights = employees)

model3_svc <- lm(log(real_compensation) ~ log(real_labor_productivity),
                 data = df %>% filter(sector == "Services"),
                 weights = employees)

summary(model3_mfg)
summary(model3_svc)

df_early <- df_early %>%
  mutate(sector = case_when(
    industry_code == "C" ~ "Manufacturing",
    industry_code %in% c("G","H","I","J","K","L","M","N","P","Q","R","S") ~ "Services",
    TRUE ~ "Other"
  ))

df_late <- df_late %>%
  mutate(sector = case_when(
    industry_code == "C" ~ "Manufacturing",
    industry_code %in% c("G","H","I","J","K","L","M","N","P","Q","R","S") ~ "Services",
    TRUE ~ "Other"
  ))

model3_mfg_early <- lm(log(real_compensation) ~ log(real_labor_productivity),
                 data = df_early %>% filter(sector == "Manufacturing"),
                 weights = employees)

model3_svc_early <- lm(log(real_compensation) ~ log(real_labor_productivity),
                 data = df_early %>% filter(sector == "Services"),
                 weights = employees)

model3_mfg_late<- lm(log(real_compensation) ~ log(real_labor_productivity),
                       data = df_late %>% filter(sector == "Manufacturing"),
                       weights = employees)

model3_svc_late <- lm(log(real_compensation) ~ log(real_labor_productivity),
                       data = df_late %>% filter(sector == "Services"),
                       weights = employees)



# model1 extended: labour share interms of different industry
df %>%
  group_by(industry_code, industry_name) %>%
  summarise(
    avg_labour_share = mean(labour_share_gva, na.rm = TRUE)
  ) %>%
  arrange(desc(avg_labour_share))

