df<-read_csv("data/clean/census_clean.csv")
cpi<-read_csv("data/clean/tw_cpi.csv") %>%
  filter(year %in% c(1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021))

