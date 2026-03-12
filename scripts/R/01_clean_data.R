library(tidyverse)
df_raw<-read.csv("data/clean/tw_industry_census.csv")
#check data format
glimpse(df_raw)
head(df_raw)
summary(df_raw)

# change from wide to long, each row corresponding to a year
df_long<-df_raw %>% #it will save the result for the corresponding step
  select(-change_2016_to_2021_pct) %>% #remove the last column
  pivot_longer(cols = starts_with("X"),names_to="year",values_to = "value") %>% # change from wide format to long format, for better processing in R
  mutate(year=as.integer(str_remove(year,"X"))) #remove the X str and change to int
  
  

#change from long to wide, merge all the values to the corresponding year to column
df_wide<-df_long %>%
  select(-unit)%>% #remove "unit" column
  #use id_cols to identify the only cols.
  pivot_wider(id_cols = c(industry_code, industry_name, year),names_from="indicator_id", values_from="value")
  

df_clean<-df_wide %>%
  rename(
    enterprises                 = `1`,
    employees                   = `2`,
    labor_compensation          = `3`,
    revenue                     = `4`,
    expenditure                 = `5`,
    gross_output                = `6`,
    value_added                 = `7`,
    assets                      = `8`,
    fixed_assets                = `9`,
    avg_employees_per_firm      = `10(1)`,
    avg_assets_per_firm         = `10(2)`,
    capital_labor_ratio         = `11`,
    labor_productivity          = `12`,
    capital_productivity_assets = `13(1)`,
    capital_productivity_fixed  = `13(2)`,
    labor_cost_ratio            = `14`,
    value_added_rate            = `15(1)`,
    profit_rate                 = `15(2)`,
    asset_turnover              = `15(3)`
  )
write_csv(df_clean, "data/clean/census_clean.csv")


  

  
  

