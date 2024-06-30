# ESP_calculations

Fluid Properties vs. Pressure, ESP Pressure Difference Analysis (PIPESIM & Unifloc VBA).ipynb - файл расчетами

В ходе рассчетов используются следующие модели PIPESIM:
1) Model_fluid_property_analysis.pips - используется для анализа вязкости, ГС, объемного коэф., плотности нефти в зависимости от давления (MODEL_PATH); 
2) ESP_P_DIS_water.pips - для анализа P_dis, в качестве флюида используется вода (PIPESIM_ESP_P_DIS_WATER_MODEL_PATH);
3) ESP_P_DIS_oil.pips - для анализа P_dis, в качестве флюида используется нефть (PIPESIM_MODEL_PATH_ESP_P_DIS_OIL_BASE);
4) Unifloc_calc_ESP_P_DIS_WATER.xlsx - для проверки расчета P_dis для воды непосредственно в Excel с использованием Unifloc VBA.
