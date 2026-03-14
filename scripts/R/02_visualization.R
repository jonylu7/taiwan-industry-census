library(tidyverse)

df <- read_csv("data/clean/census_clean.csv")
cpi_data<-read_csv("data/clean/tw_cpi.csv") %>%
  filter(year %in% c(1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021))

#step1: overall analysis

variables<-c("labor_compensation", "labor_productivity","capital_labor_ratio","labor_cost_ratio",     # 14
             "profit_rate",           # 15(2)
             "value_added_rate",      # 15(1)
             "value_added")
for (v in variables){
p<-df %>%
  ggplot(aes(x = year, y = .data[[v]], color = industry_name)) +
  geom_line() +
  geom_point() +
  labs(
    title = paste(v, "by Industry (1981-2021)"),
    x = "Year",
    y = v,
    color = "Industry"
  ) +
  theme_minimal()

ggsave(paste0("output/figures/",paste("all_",v), ".png"),
       p, width = 12, height = 6)
}

#step 2: labor comps adjust to CPI

df<-df %>%
  left_join(cpi_data, by = "year") %>%
  mutate(
    real_compensation= labor_compensation / cpi_index * 100/1000,#/1000 is for formating
    real_labor_productivity  = labor_productivity / cpi_index * 100,
    labour_share_gva = (labor_compensation * employees) / (value_added * 10000))
p2<-df %>%
ggplot(aes(x = year, y = real_compensation, color = industry_name)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Real Labor Compensation by by Industry (1981-2021)",
    x = "Year",
    y = "thounsands NTD",
    color = "Industry"
  ) +
  theme_minimal()

ggsave(paste0("output/figures/","real_labor_comp", ".png"),
       p2, width = 12, height = 6)


#step 3: labor productivity adjust to CPI
p2<-df %>%
  ggplot(aes(x = year, y = real_labor_productivity, color = industry_name)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Real Labor Productivity by by Industry (1981-2021)",
    x = "Year",
    y = "thounsands NTD",
    color = "Industry"
  ) +
  theme_minimal()

ggsave(paste0("output/figures/","real_labor_prod", ".png"),
       p2, width = 12, height = 6)



# profit and labor share graph
df_share <- df %>%
  group_by(year) %>%
  summarise(
    avg_labor_share = weighted.mean(labour_share_gva,w=employees, na.rm = TRUE),
    avg_profit_rate = weighted.mean(profit_rate,w=employees, na.rm = TRUE)
  )

df_share_long <- df_share %>%
  pivot_longer(cols = c(avg_labor_share, avg_profit_rate),
               names_to = "variable", values_to = "value")

p3<-ggplot(df_share_long, aes(x = year, y = value, color = variable)) +
  geom_line(linewidth = 1.2) +
  geom_vline(xintercept = 2001, linetype = "dashed", color = "gray50") +
  annotate("text", x = 2002, y = max(df_share_long$value, na.rm = TRUE),
           label = "2001", hjust = 0) +
  labs(title = "Labour Share vs Profit Rate 1981-2021",
       y = "Percentage (%)", x = "Year") +
  scale_color_discrete(labels = c("Labour Share", "Profit Rate")) +
  theme_minimal()

ggsave(paste0("output/figures/","labor_share_gva_profit", ".png"),
       p3, width = 12, height = 6)