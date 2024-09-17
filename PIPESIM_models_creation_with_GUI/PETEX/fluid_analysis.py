
#----------------------------------------------------------------------------------
# Импорт необходимых библиотек и модулей / Import necessary libraries and modules
# ----------------------------------------------------------------------------------

# Общие библиотеки / General Libraries
import os
import pandas as pd 
import numpy as np
from collections import defaultdict
import json
import shutil
# import sys # print(sys.executable)
from dash import Dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

# Pipesim библиотеки / Pipesim Libraries
from sixgill.pipesim import Model
from sixgill.definitions import Parameters, SystemVariables, ProfileVariables, Constants, Units

# Unifloc VBA библиотеки и настройка / Unifloc VBA Libraries and Setup
unifloc_path = r'D:\Github\unifloc_vba' # прописываем путь к репозиторию Unifloc VBA
unifloc_xlam = unifloc_path + r'\UniflocVBA_7.xlam'
print('Путь к надстройке Unifloc VBA: '+ unifloc_xlam)

import sys
sys.path.insert(0, unifloc_path) # добавим в путь поиска пакетов python папку, где находится репозиторий Unifloc VBA
import unifloc_vba_python_api.python_api as unifloc # импортируем python_api для работы с Unifloc VBA

unf = unifloc.API(unifloc_xlam) # создаем объект имеющий доступ к расчетным модулям Unifloc VBA

print('Объект unf обеспечивает доступ к API Unifloc VBA.')

# ----------------------------------------------------------------------------------
# Задание расположения моделей
# ----------------------------------------------------------------------------------

# Установим путь к модели PIPESIM для расчета вязкости, ГС, объемного коэф., плотности
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Model_fluid_properties_analysis.pips")
# Установим путь к базовой модели для расчета p_dis, в качастве флюида используется нефть (используется модель ESP_P_DIS_oil.pips)
# Это базовая модель, в которой будем проводить изменения
PIPESIM_MODEL_PATH_ESP_P_DIS_OIL_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ESP_P_DIS_oil.pips")
# Установим путь к модели PIPESIM для расчета p_dis, в качастве флюида используется вода (используется модель ESP_P_DIS_water.pips)
PIPESIM_ESP_P_DIS_WATER_MODEL_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ESP_P_DIS_water.pips")
 
# ----------------------------------------------------------------------------------
# Задание расположения файла с результатами
# ----------------------------------------------------------------------------------
current_directory = os.path.dirname(os.path.abspath(__file__))
results_folder_name = "Results" # Задаем имя папки, в которой будем хранить результаты
results_directory = os.path.join(current_directory, results_folder_name) # Создаем в директории текущего ".py" файла новую папку, в которой будем хранить результаты
results_file_name = "Results.json" # Задаем имя файла, в котором будем хранить результаты
results_file_path = os.path.join(results_directory, results_file_name) # Задаем полный путь к файлу, в котором будем хранить результаты

# Проверим, существует ли уже папка с результами или нет
if os.path.exists(results_directory):
    shutil.rmtree(results_directory)
    print("Папка с уже имеющиемися результатами расчета удалена.")

os.makedirs(results_directory)
print("Папка для хранения результатов расчета создана.")


# ----------------------------------------------------------------------------------
# Задание основных ключевых слов для записи результатов в словарь
# ----------------------------------------------------------------------------------
pipesim_modeling_FA_status = True # проводим ли расчет модели PIPESIM в рамках анализа свойств (Fluid Analysis - FA) или нет
unifloc_modeling_FA_status = True # проводим ли расчет модели Unifloc в рамках FA или нет
pipesim_modeling_P_dis_WATER_status = True # проводим ли расчет модели PIPESIM в рамках анализа работы ЭЦН (флюид: вода - ESP_W) или нет
unifloc_modeling_P_dis_WATER_status = True # проводим ли расчет модели Unifloc в рамках анализа ESP_W или нет
pipesim_modeling_P_dis_OIL_status = True # проводим ли расчет модели PIPESIM в рамках анализа работы ЭЦН (флюид: нефть - ESP_O) или нет
                                          # в этом расчете резльтаты PIP сравниваются с Unifloc на одном графике
unifloc_modeling_P_dis_OIL_status = True # проводим ли расчет модели Unifloc в рамках анализа ESP_O или нет; 
                                          # в этом расчете резльтаты PIP сравниваются с Unifloc на одном графике
pipesim_modeling_P_dis_OIL_dif_GOR_status = True # роводим ли расчет модели PIPESIM в рамках анализа работы ЭЦН (флюид: нефть - ESP_O) или нет
                                                  # в этом расчете анализируем влияние GOR на НРХ только для модели PIP
unifloc_modeling_P_dis_OIL_dif_GOR_status = True # проводим ли расчет модели Unifloc в рамках анализа ESP_O или нет
                                                  # в этом расчете анализируем влияние GOR на НРХ только для модели Unifloc

results_data = defaultdict(lambda: defaultdict(dict)) # создаем многоуровневый словарь для хранения результатов расчета

resuts_key_fluid_analysis = "Fluid_Analysis" # Ключ для расчетных значений в рамках FA
resuts_key_p_dis_water = "P_dis_water_case" # Ключ для расчетных значений в рамках анализа расчета перепада давления, создаваемым ЭЦН, при прокачке воды
resuts_key_p_dis_oil = "P_dis_oil_case" # Ключ для расчетных значений в рамках анализа расчета перепада давления, создаваемым ЭЦН, при прокачке ГЖС
resuts_key_p_dis_pipesim_dif_gor = "P_dis_pipesim_case_dif_gor"
resuts_key_p_dis_unifloc_dif_gor = "P_dis_unifloc_case_dif_gor"

results_key_pipesim = "PIPESIM" # Ключ, который характерезует данные, как рассчитанные в PIPESIM 
results_key_unifloc = "Unifloc" # Ключ, который характерезует данные, как рассчитанные в Unifloc

# Задаем ключи для параметров
pressure_key_bara = "pressure_bara"
pressure_key_atma = "pressure_atma"
viscosity_key_cp = "viscosity_cP"
temperature_key_C = "temperature_C"
solution_gas_key_m3m3 = "solution_gas_C"
fvf_key = "formation_volume_factor"
density_key_kg_m3 = "denstiy_kg_m3"
liquid_flowrate_key_sm3_day = "liquid_flowrate_sm3_day"

p_dis_oil_key = "Pdis_vs_Q_by_GOR" # ключ для задания зависимости Pdis vs Qliq для разных значения GOR, используется для расчетов в рамках анализа ESP_O

empty_key = "Empty"
empty_value = "Empty"


# ----------------------------------------------------------------------------------
# Моделирование в PIPESIM / Modeling in PIPESIM
# ----------------------------------------------------------------------------------

if pipesim_modeling_FA_status == True:
    print("--"*40)
    print("Комментарии ниже относятся к расчетной части PIPESIM.")
    
    # Открытие модели
    model = Model.open(MODEL_PATH, Units.METRIC)
    model.close()
    model = Model.open(MODEL_PATH, units=Units.METRIC)

    model.set_value(context="Black_oil_fluid", 
                    parameter = Parameters.BlackOilFluid.SinglePointCalibration.BUBBLEPOINTSATGAS_VALUE, 
                    value=100)

    studyptsim = model.tasks.ptprofilesimulation.get_conditions("Well",
                "Study 1")


    profile_variables = [
                            ProfileVariables.TEMPERATURE,
                            ProfileVariables.PRESSURE,
                            ProfileVariables.VISCOSITY_OIL_INSITU, 
                            ProfileVariables.SOLUTION_GAS_IN_OIL_INSITU,
                            ProfileVariables.FORMATION_VOLUME_FACTOR_OIL_INSITU,
                            ProfileVariables.DENSITY_OIL_INSITU,
    ]

    results = model.tasks.ptprofilesimulation.run(
                producer="Well",
                profile_variables=profile_variables, 
    )

    print("--"*40)

    pressure_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.PRESSURE] # bara
    viscosity_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.VISCOSITY_OIL_INSITU] # cP
    temperature_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.TEMPERATURE] # C
    solution_gas_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.SOLUTION_GAS_IN_OIL_INSITU] # m3/m3
    fvf_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.FORMATION_VOLUME_FACTOR_OIL_INSITU]
    density_data_pipesim_FA = results.profile[next(iter(results.profile.keys()))][ProfileVariables.DENSITY_OIL_INSITU]
    
    print("Данные из модели PIPESIM получены.")

    # сохраняем данные PIPESIM 
    results_data[resuts_key_fluid_analysis][results_key_pipesim][pressure_key_bara] = pressure_data_pipesim_FA
    results_data[resuts_key_fluid_analysis][results_key_pipesim][viscosity_key_cp] = viscosity_data_pipesim_FA
    results_data[resuts_key_fluid_analysis][results_key_pipesim][temperature_key_C] = temperature_data_pipesim_FA
    results_data[resuts_key_fluid_analysis][results_key_pipesim][solution_gas_key_m3m3] = solution_gas_data_pipesim_FA
    results_data[resuts_key_fluid_analysis][results_key_pipesim][fvf_key] = fvf_data_pipesim_FA
    results_data[resuts_key_fluid_analysis][results_key_pipesim][density_key_kg_m3] = density_data_pipesim_FA

    print(f"Результаты расчета в рамках FA в PIPESIM выгружены в '{results_file_name}' в папке '{results_folder_name}'.")

else:

    results_data[resuts_key_fluid_analysis][results_key_pipesim][empty_key] = empty_value

    print("Расчет модели PIPESIM в рамках аназила свойств флюида не был выполнен.\n \
           Рассчетные значения не были выгружены.")
    
# ----------------------------------------------------------------------------------
# Моделирование в Unifloc VBA в рамках FA / Modeling in Unifloc VBA
# ----------------------------------------------------------------------------------

if unifloc_modeling_FA_status == True:
    # Задаем флюид
    fluid = unf.encode_PVT(gamma_gas=0.6, 
                        gamma_oil=0.86, 
                        gamma_wat=1.1, 
                        rsb_m3m3=100, 
                        pb_atma=130, 
                        t_res_C=80, 
                        bob_m3m3=1.2, 
                        muob_cP=0.6, 
                        PVT_corr_set=0)
    
    temperature_unf = 30 # значение температуры такое же, как и в модели PIPESIM

    try:
        pressure_data_unifloc_FA = [pressure * 0.9869234 for pressure in  pressure_data_pipesim_FA] # добавлен перевод (bara) в (atma) для корректного расчета в Unifloc
        print("Список значений для давлений из PIPESIM рассчитан, используем его за основу при расчетах FA в Unifloc.")
    except NameError:
        print("Список значений для давлений из PIPESIM отсутсвует. Создаем произвольный список с 15 значениями от 10 до 250.")
        pressure_data_unifloc_FA = list(np.linspace(10, 250, 15))
    
    # Расчет вязкости с использованием соответствующей функции в Unifloc
    calculated_unf_viscosity = [unf.PVT_mu_oil_cP(p, temperature_unf, fluid) for p in pressure_data_unifloc_FA]
    
    # Расчет газосодержания с использованием соответствующей функции в Unifloc
    calculated_solution_gas_unifloc = [unf.PVT_rs_m3m3(p, temperature_unf, fluid)  for p in pressure_data_unifloc_FA]

    # Расчет объемного коэффициента с использованием соответствующей функции в Unifloc
    calculated_fvf_unifloc = [unf.PVT_bo_m3m3(p, temperature_unf, fluid) for p in pressure_data_unifloc_FA]

    # Расчет лотности с использованием соответствующей функции в Unifloc
    calculated_density_unifloc = [unf.PVT_rho_oil_kgm3(p, temperature_unf, fluid) for p in pressure_data_unifloc_FA]

    results_data[resuts_key_fluid_analysis][results_key_unifloc][pressure_key_atma] = pressure_data_unifloc_FA
    results_data[resuts_key_fluid_analysis][results_key_unifloc][viscosity_key_cp] = calculated_unf_viscosity
    results_data[resuts_key_fluid_analysis][results_key_unifloc][solution_gas_key_m3m3] = calculated_solution_gas_unifloc
    results_data[resuts_key_fluid_analysis][results_key_unifloc][fvf_key] = calculated_fvf_unifloc
    results_data[resuts_key_fluid_analysis][results_key_unifloc][density_key_kg_m3] = calculated_density_unifloc

    print(f"Результаты расчета в рамках FA в Unifloc выгружены в '{results_file_name}' в папке '{results_folder_name}'.")

else:

    results_data[resuts_key_fluid_analysis][results_key_unifloc][empty_key] = empty_value

    print("Расчет модели Unifloc в рамках аназила свойств флюида не был выполнен. \
           Рассчетные значения не были выгружены.")


# ----------------------------------------------------------------------------------
# Моделирование расчета Discharge Pressure в PIPESIM (флюид - вода) / 
# ----------------------------------------------------------------------------------
if pipesim_modeling_P_dis_WATER_status == True:
    print("--"*40)
    print("Комментарии ниже относятся к расчетной части PIPESIM.")
    # Откроем модель PIPESIM
    pipesim_model = Model.open(PIPESIM_ESP_P_DIS_WATER_MODEL_PATH, Units.METRIC)
    print(pipesim_model.about())

    # Список переменных профиля для PIPESIM
    pipesim_profile_variables = [
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.ELEVATION,
        ProfileVariables.TOTAL_DISTANCE,
    ]

    # Диапазон расхода жидкости
    pipesim_liquid_flowrates = list(range(5, 300, 20))

    # Список для хранения значений давления на выходе
    pipesim_p_dis_values = []

    # Рассчет давлений
    for liquid_flow_rate in pipesim_liquid_flowrates:
        parameters = {
            Parameters.PTProfileSimulation.INLETPRESSURE: 151.9875,  # 150 (atma) from Unifloc converted to (bara) in PIPESIM
            Parameters.PTProfileSimulation.LIQUIDFLOWRATE: liquid_flow_rate,
            Parameters.PTProfileSimulation.FLOWRATETYPE: Constants.FlowRateType.LIQUIDFLOWRATE,
            Parameters.PTProfileSimulation.CALCULATEDVARIABLE: Constants.CalculatedVariable.OUTLETPRESSURE,
        }

        # Запуск симуляции и получение результатов
        print("Running PT profile simulation in PIPESIM")
        results = pipesim_model.tasks.ptprofilesimulation.run(
            producer="Well",
            parameters=parameters,
            profile_variables=pipesim_profile_variables
        )

        # Получение значения давления на выходе из профиля (результата расчета)
        for case, profile in results.profile.items():
            profile_df = pd.DataFrame.from_dict(profile)
            pressure = profile_df[profile_df["BranchEquipment"] == 'Esp1']["Pressure"].iloc[0]*0.986923 # converted to (atma)

        # Добавление давление в созданный ранее лист
        pipesim_p_dis_values.append(pressure)

    print("--"*40)

    results_data[resuts_key_p_dis_water][results_key_pipesim][pressure_key_atma] = pipesim_p_dis_values
    results_data[resuts_key_p_dis_water][results_key_pipesim][liquid_flowrate_key_sm3_day] = pipesim_liquid_flowrates

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - вода) в PIPESIM выгружены в '{results_file_name}' в папке '{results_folder_name}'.")

    # Закрытие модели PIPESIM
    pipesim_model.close()

else:
    results_data[resuts_key_p_dis_water][results_key_pipesim][empty_key] = empty_value
    print("Расчет модели PIPESIM рамках расчета давления на выходе из ЭЦН (флюид - вода) не был выполнен. \
           Рассчетные значения не были выгружены.")

if unifloc_modeling_P_dis_WATER_status == True:
    # Диапазон расхода жидкости для Source 2 (Unifloc)
    try:
        unifloc_liquid_flowrates = pipesim_liquid_flowrates.copy()
        print("Список значений расходов взят такой же как и при расчете в PIPESIM, используем его за основу при расчетах в рамках кейса ESP_W.")
    except NameError:
        print("Список значений для расходов из PIPESIM отсутсвует. Создаем произвольный список 5-300 с шагом 20.")
        unifloc_liquid_flowrates = list(range(5, 300, 20))

    # Параметры PVT для модели ЭЦН
    gamma_gas_value = 0.6
    gamma_oil_value = 0.86
    gamma_wat_value = 1.02
    rsb_m3m3_value = 120
    pb_atma_value = 130
    t_res_C_value = 80
    bob_m3m3_value = 1.2
    muob_cP_value = 0.6
    PVT_corr_set_value = 0

    # Создание модели ЭЦН с использованием Unifloc
    esp_params = unf.encode_ESP_pump(
        q_nom_sm3day=120,
        head_nom_m=2000,
        freq_nom_Hz=50,
        num_stages=10,
        calibr_head=1,
        calibr_rate=1,
        calibr_power=1,
        gas_correct_model=1,
        gas_correct_stage_by_stage=0,
        dnum_stages_integrate=1
    )

    # Рассчет давления p_dis для Unifloc
    unifloc_p_dis_values = []

    for q_liq_value in unifloc_liquid_flowrates:
        # Создание PVT_ESP с использованием заданных параметров
        PVT_ESP = unf.encode_PVT(
            gamma_gas=gamma_gas_value,
            gamma_oil=gamma_oil_value,
            gamma_wat=gamma_wat_value,
            rsb_m3m3=rsb_m3m3_value,
            pb_atma=pb_atma_value,
            t_res_C=t_res_C_value,
            bob_m3m3=bob_m3m3_value,
            muob_cP=muob_cP_value,
            PVT_corr_set=PVT_corr_set_value
        )

        # Создание feed_esp для расчета p_dis
        feed_esp = unf.encode_feed(
            q_liq_sm3day=q_liq_value,
            fw_perc=100,  # Процентная вода
            rp_m3m3=120,
            q_gas_free_sm3day=0,
            fluid=PVT_ESP
        )

        # Расчет p_dis с использованием модели ЭЦН из Unifloc
        p_dis = unf.ESP_p_atma(
            p_calc_atma=150,  # Расчетное давление
            t_intake_C=80,    # Температура на входе
            t_dis_C=80,       # Температура на выходе
            feed=feed_esp,
            esp_json=esp_params,
            freq_Hz=48.5,
            calc_along_flow=1,
            param=1,
            h_mes_top=2000
        )

        # Добавление рассчитанного значения p_dis в список
        unifloc_p_dis_values.append(p_dis)

    results_data[resuts_key_p_dis_water][results_key_unifloc][pressure_key_atma] = unifloc_p_dis_values
    results_data[resuts_key_p_dis_water][results_key_unifloc][liquid_flowrate_key_sm3_day] = unifloc_liquid_flowrates

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - вода) в Unifloc выгружены в '{results_file_name}' в папке '{results_folder_name}'.")
else:
    results_data[resuts_key_p_dis_water][results_key_unifloc][empty_key] = empty_value
    print("Расчет модели Unifloc рамках расчета давления на выходе из ЭЦН (флюид - вода) не был выполнен. \
           Рассчетные значения не были выгружены.")


# ----------------------------------------------------------------------------------
# Моделирование расчета Discharge Pressure в PIPESIM (флюид - нефть). 
# Результаты будут сравнены с Unifloc на одном грвфике. /
# ----------------------------------------------------------------------------------

# PIPESIM   
# gor_values_pipesim = [150]
gor_values_pipesim = list(range(50, 150, 25))
liquid_flow_rates_pipesim = list(range(5, 300, 20))
# Unifloc
rp_values_unifloc = gor_values_pipesim.copy()
liquid_flow_rates_unifloc = liquid_flow_rates_pipesim.copy()

if pipesim_modeling_P_dis_OIL_status:

    print("--"*40)
    print("Комментарии ниже относятся к расчетной части PIPESIM.")
    print("--"*40)

    # Откроем модель PIPESIM
    model = Model.open(PIPESIM_MODEL_PATH_ESP_P_DIS_OIL_BASE, Units.METRIC)
    # print(pipesim_model.about())

    profile_variables = [
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.ELEVATION,
        ProfileVariables.TOTAL_DISTANCE,
    ]

    gor_Pdis_Q_pipesim = defaultdict(dict)

    # Create pairs of plots for each GOR value from both sources
    for gor_pip in gor_values_pipesim:
        p_dis_values_pipesim = []  # List to store pressure values
        
        # Source 1 (PIPESIM)
        model.set_value(
            context="Oil_ESP",
            parameter=Parameters.BlackOilFluid.GOR,
            value=gor_pip
        )

        # random_color = random.choice(all_colors)
        # model.save(MODEL_FOLDER_PATH_ESP_P_DIS_OIL + "\ESP_GOR_" + str(gor_source1) + ".pips")
        
        for liquid_flow_rate in liquid_flow_rates_pipesim:
            parameters = {
                Parameters.PTProfileSimulation.INLETPRESSURE: 151.9875,  # 150 (atma) Unifloc converted to (bara) PIPESIM
                Parameters.PTProfileSimulation.LIQUIDFLOWRATE: liquid_flow_rate,
                Parameters.PTProfileSimulation.FLOWRATETYPE: Constants.FlowRateType.LIQUIDFLOWRATE,
                Parameters.PTProfileSimulation.CALCULATEDVARIABLE: Constants.CalculatedVariable.OUTLETPRESSURE,
            }

            # Run the simulation and print out the results
            print("Running PT profile simulation")
            results = model.tasks.ptprofilesimulation.run(producer="Well",
                                                        parameters=parameters,
                                                        profile_variables=profile_variables)

            # Profile results
            for case, profile in results.profile.items():
                profile_df = pd.DataFrame.from_dict(profile)
                pressure = profile_df[profile_df["BranchEquipment"] == 'Esp1']["Pressure"].iloc[0] * 0.986923 # converted to (atma)
                print("Pressure: ", pressure)

            # Append pressure value to the list
            p_dis_values_pipesim.append(pressure)

        # TO DO: изменить способ хранения резульаттов для разных GOR
        gor_Pdis_Q_pipesim[gor_pip][pressure_key_atma] = p_dis_values_pipesim
        gor_Pdis_Q_pipesim[gor_pip][liquid_flowrate_key_sm3_day] = liquid_flow_rates_pipesim

    print("--"*40)
    print("Комментарии относящиеся к расчетной части PIPESIM закончены.")
    print("--"*40)

    results_data[resuts_key_p_dis_oil][results_key_pipesim][p_dis_oil_key] = gor_Pdis_Q_pipesim

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - нефть) в PIPESIM выгружены в '{results_file_name}' в папке '{results_folder_name}'.")

    # Закрываем модель PIPESIM
    model.close()
else:
    results_data[resuts_key_p_dis_oil][results_key_pipesim][empty_key] = empty_value
    print("Расчет модели PIPESIM рамках расчета давления на выходе из ЭЦН (флюид - нефть) не был выполнен. \
           Рассчетные значения не были выгружены.")

# ----------------------------------------------------------------------------------
# Моделирование расчета Discharge Pressure в Unifloc (флюид - нефть). 
# Результаты будут сравнены с PIPESIM на одном графике. / 
# ----------------------------------------------------------------------------------
if unifloc_modeling_P_dis_OIL_status:

    gor_Pdis_Q_unifloc = defaultdict(dict)
    
    # PVT parameters for ESP model
    gamma_gas_value = 0.6
    gamma_oil_value = 0.86
    gamma_wat_value = 1.1
    rsb_m3m3_value = 120
    pb_atma_value = 130
    t_res_C_value = 80
    bob_m3m3_value = 1.2
    muob_cP_value = 0.6
    PVT_corr_set_value = 0

    # Fluid flow parameters
    q_liq_sm3day_value = 50
    fw_perc_value = 0
    rp_m3m3_value = None
    q_gas_free_sm3day_value = 0

    # ESP parameters
    ESP_q_nom_value = 120
    ESP_head_nom_value = 2000
    freq_nom_value = 48.5
    num_stages_value = 10
    calibr_head_value = 1
    calibr_rate_value = 1
    calibr_power_value = 1 
    gas_correct_model_value = 1 
    gas_correct_stage_by_stage_value = 0
    dnum_stages_integrate_value = 1

    # Parameters for calculating p_dis
    p_calc_atma_value = 150
    t_intake_C_value = 80
    t_dis_C_value = 80
    freq_Hz_value = 50
    calc_along_flow_value = 1
    param_value = 1
    h_mes_top_value = 2000

    # Encode ESP pump
    esp = unf.encode_ESP_pump(
        q_nom_sm3day=ESP_q_nom_value,
        head_nom_m=ESP_head_nom_value,
        freq_nom_Hz=freq_nom_value,
        num_stages=num_stages_value,
        calibr_head=calibr_head_value,
        calibr_rate=calibr_rate_value,
        calibr_power=calibr_power_value,
        gas_correct_model=gas_correct_model_value,
        gas_correct_stage_by_stage=gas_correct_stage_by_stage_value,
        dnum_stages_integrate=dnum_stages_integrate_value
    )

    for gor_source2 in rp_values_unifloc:
        print(gor_source2)
        p_dis_values_unifloc = []

        # Calculate p_dis values for Source 2
        for q_liq_value in liquid_flow_rates_unifloc:
            
            # Create PVT_ESP using specified parameters
            PVT_ESP = unf.encode_PVT(
                gamma_gas=gamma_gas_value,
                gamma_oil=gamma_oil_value,
                gamma_wat=gamma_wat_value,
                rsb_m3m3=rsb_m3m3_value,
                pb_atma=pb_atma_value,
                t_res_C=t_res_C_value,
                bob_m3m3=bob_m3m3_value,
                muob_cP=muob_cP_value,
                PVT_corr_set=PVT_corr_set_value
            )
            
            feed_esp = unf.encode_feed(
                q_liq_sm3day=q_liq_value,
                fw_perc=fw_perc_value,
                rp_m3m3=gor_source2,
                q_gas_free_sm3day=q_gas_free_sm3day_value,
                fluid=PVT_ESP
            )

            p_dis = unf.ESP_p_atma(
                p_calc_atma=p_calc_atma_value,
                t_intake_C=t_intake_C_value,
                t_dis_C=t_dis_C_value,
                feed=feed_esp,
                esp_json=esp,
                freq_Hz=freq_Hz_value,
                calc_along_flow=calc_along_flow_value,
                param=param_value,
                h_mes_top=h_mes_top_value
            )
            
            p_dis_values_unifloc.append(p_dis)

        # TO DO: изменить способ хранения резульаттов для разных GOR
        
        gor_Pdis_Q_unifloc[gor_source2][pressure_key_atma] = p_dis_values_unifloc
        gor_Pdis_Q_unifloc[gor_source2][liquid_flowrate_key_sm3_day] = liquid_flow_rates_unifloc

    results_data[resuts_key_p_dis_oil][results_key_unifloc][p_dis_oil_key] = gor_Pdis_Q_unifloc

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - нефть) в Unifloc выгружены в '{results_file_name}' в папке '{results_folder_name}'.")
else:
    results_data[resuts_key_p_dis_oil][results_key_unifloc][empty_key] = empty_value
    print("Расчет модели Unifloc рамках расчета давления на выходе из ЭЦН (флюид - нефть) не был выполнен. \
           Рассчетные значения не были выгружены.")

# ----------------------------------------------------------------------------------
# Моделирование расчета Discharge Pressure только в PIPESIM (флюид - нефть) при разных GOR.
# На графике будут отображены только резульаты моделирования в PIPESIM. / 
# ----------------------------------------------------------------------------------
gor_values_pipesim_dif_gor = list(range(50, 500, 50))
liquid_flow_rates_pipesim_dif_gor = list(range(5, 300, 20))
gor_values_unifloc_dif_gor = gor_values_pipesim_dif_gor.copy()
liquid_flow_rates_unifloc_dif_gor = liquid_flow_rates_pipesim_dif_gor.copy()

if pipesim_modeling_P_dis_OIL_dif_GOR_status:

    print("--"*40)
    print("Комментарии ниже относятся к расчетной части PIPESIM.")
    print("--"*40)

    # Откроем модель PIPESIM
    model = Model.open(PIPESIM_MODEL_PATH_ESP_P_DIS_OIL_BASE, Units.METRIC)
    # print(pipesim_model.about())

    profile_variables = [
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.ELEVATION,
        ProfileVariables.TOTAL_DISTANCE,
    ]

    gor_Pdis_Q_pipesim = defaultdict(dict)

    # Create pairs of plots for each GOR value from both sources
    for gor_pipesim in gor_values_pipesim_dif_gor:
        p_dis_values_pipesim = []  # List to store pressure values
        
        # Source 1 (PIPESIM)
        model.set_value(
            context="Oil_ESP",
            parameter=Parameters.BlackOilFluid.GOR,
            value=gor_pipesim
        )

        # random_color = random.choice(all_colors)
        # model.save(MODEL_FOLDER_PATH_ESP_P_DIS_OIL + "\ESP_GOR_" + str(gor_source1) + ".pips")
        
        for liquid_flow_rate in liquid_flow_rates_pipesim_dif_gor:
            parameters = {
                Parameters.PTProfileSimulation.INLETPRESSURE: 151.9875,  # 150 (atma) Unifloc converted to (bara) PIPESIM
                Parameters.PTProfileSimulation.LIQUIDFLOWRATE: liquid_flow_rate,
                Parameters.PTProfileSimulation.FLOWRATETYPE: Constants.FlowRateType.LIQUIDFLOWRATE,
                Parameters.PTProfileSimulation.CALCULATEDVARIABLE: Constants.CalculatedVariable.OUTLETPRESSURE,
            }

            # Run the simulation and print out the results
            print("Running PT profile simulation")
            results = model.tasks.ptprofilesimulation.run(producer="Well",
                                                        parameters=parameters,
                                                        profile_variables=profile_variables)

            # Profile results
            for case, profile in results.profile.items():
                profile_df = pd.DataFrame.from_dict(profile)
                pressure = profile_df[profile_df["BranchEquipment"] == 'Esp1']["Pressure"].iloc[0] * 0.986923 # converted to (atma)
                print("Pressure: ", pressure)

            # Append pressure value to the list
            p_dis_values_pipesim.append(pressure)

        # TO DO: изменить способ хранения резульаттов для разных GOR
        gor_Pdis_Q_pipesim[gor_pipesim][pressure_key_atma] = p_dis_values_pipesim
        gor_Pdis_Q_pipesim[gor_pipesim][liquid_flowrate_key_sm3_day] = liquid_flow_rates_pipesim

    print("--"*40)
    print("Комментарии относящиеся к расчетной части PIPESIM закончены.")
    print("--"*40)

    results_data[resuts_key_p_dis_pipesim_dif_gor][results_key_pipesim][p_dis_oil_key] = gor_Pdis_Q_pipesim

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - нефть) в PIPESIM выгружены в '{results_file_name}' в папке '{results_folder_name}'.")

    # Закрываем модель PIPESIM
    model.close()
else:
    pass


# ----------------------------------------------------------------------------------
# Моделирование расчета Discharge Pressure только в Unifloc (флюид - нефть) при разных GOR.
# На графике будут отображены только резульаты моделирования в Unifloc. / 
# ----------------------------------------------------------------------------------
if unifloc_modeling_P_dis_OIL_dif_GOR_status:
    
    gor_Pdis_Q_unifloc = defaultdict(dict)
    
    # PVT parameters for ESP model
    gamma_gas_value = 0.6
    gamma_oil_value = 0.86
    gamma_wat_value = 1.1
    rsb_m3m3_value = 120
    pb_atma_value = 130
    t_res_C_value = 80
    bob_m3m3_value = 1.2
    muob_cP_value = 0.6
    PVT_corr_set_value = 0

    # Fluid flow parameters
    q_liq_sm3day_value = 50
    fw_perc_value = 0
    rp_m3m3_value = None
    q_gas_free_sm3day_value = 0

    # ESP parameters
    ESP_q_nom_value = 120
    ESP_head_nom_value = 2000
    freq_nom_value = 48.5
    num_stages_value = 10
    calibr_head_value = 1
    calibr_rate_value = 1
    calibr_power_value = 1 
    gas_correct_model_value = 1 
    gas_correct_stage_by_stage_value = 0
    dnum_stages_integrate_value = 1

    # Parameters for calculating p_dis
    p_calc_atma_value = 150
    t_intake_C_value = 80
    t_dis_C_value = 80
    freq_Hz_value = 50
    calc_along_flow_value = 1
    param_value = 1
    h_mes_top_value = 2000

    # Encode ESP pump
    esp = unf.encode_ESP_pump(
        q_nom_sm3day=ESP_q_nom_value,
        head_nom_m=ESP_head_nom_value,
        freq_nom_Hz=freq_nom_value,
        num_stages=num_stages_value,
        calibr_head=calibr_head_value,
        calibr_rate=calibr_rate_value,
        calibr_power=calibr_power_value,
        gas_correct_model=gas_correct_model_value,
        gas_correct_stage_by_stage=gas_correct_stage_by_stage_value,
        dnum_stages_integrate=dnum_stages_integrate_value
    )

    for gor_unifloc in gor_values_unifloc_dif_gor:
        print(gor_unifloc)
        p_dis_values_unifloc = []

        # Calculate p_dis values for Source 2
        for q_liq_value in liquid_flow_rates_unifloc_dif_gor:
            
            # Create PVT_ESP using specified parameters
            PVT_ESP = unf.encode_PVT(
                gamma_gas=gamma_gas_value,
                gamma_oil=gamma_oil_value,
                gamma_wat=gamma_wat_value,
                rsb_m3m3=rsb_m3m3_value,
                pb_atma=pb_atma_value,
                t_res_C=t_res_C_value,
                bob_m3m3=bob_m3m3_value,
                muob_cP=muob_cP_value,
                PVT_corr_set=PVT_corr_set_value
            )
            
            feed_esp = unf.encode_feed(
                q_liq_sm3day=q_liq_value,
                fw_perc=fw_perc_value,
                rp_m3m3=gor_unifloc,
                q_gas_free_sm3day=q_gas_free_sm3day_value,
                fluid=PVT_ESP
            )

            p_dis = unf.ESP_p_atma(
                p_calc_atma=p_calc_atma_value,
                t_intake_C=t_intake_C_value,
                t_dis_C=t_dis_C_value,
                feed=feed_esp,
                esp_json=esp,
                freq_Hz=freq_Hz_value,
                calc_along_flow=calc_along_flow_value,
                param=param_value,
                h_mes_top=h_mes_top_value
            )
            
            p_dis_values_unifloc.append(p_dis)

        # TO DO: изменить способ хранения резульаттов для разных GOR
        
        gor_Pdis_Q_unifloc[gor_unifloc][pressure_key_atma] = p_dis_values_unifloc
        gor_Pdis_Q_unifloc[gor_unifloc][liquid_flowrate_key_sm3_day] = liquid_flow_rates_unifloc

    results_data[resuts_key_p_dis_unifloc_dif_gor][results_key_unifloc][p_dis_oil_key] = gor_Pdis_Q_unifloc

    print(f"Результаты расчета давления на выходе ЭЦН (флюид - нефть) в Unifloc выгружены в '{results_file_name}' в папке '{results_folder_name}'.")
else:
    pass


with open(results_file_path, "w") as json_file:
    json.dump(results_data, json_file, indent=3)


# # TO DO: объединить расчет с созданием моделей, т к нужно брать параметры из одного места

# # ESP parameters
# ESP_q_nom_value = 120
# ESP_head_nom_value = 2000
# freq_nom_value = 48.5
# num_stages_value = 10
# calibr_head_value = 1
# calibr_rate_value = 1
# calibr_power_value = 1 
# gas_correct_model_value = 1 
# gas_correct_stage_by_stage_value = 0
# dnum_stages_integrate_value = 1



# # Инициализация Dash приложения
# app = Dash(__name__)

# # Определение макета приложения
# app.layout = html.Div([
#     html.H1("Расчет давления на выходе ЭЦН"),

#     html.Label("Gamma Gas:"),
#     dcc.Input(id='gamma_gas', type='number', value=0.6),

#     html.Label("Gamma Oil:"),
#     dcc.Input(id='gamma_oil', type='number', value=0.86),

#     html.Label("Gamma Water:"),
#     dcc.Input(id='gamma_wat', type='number', value=1.1),

#     html.Label("RSB (m3/m3):"),
#     dcc.Input(id='rsb_m3m3', type='number', value=120),

#     html.Label("PB (Atm):"),
#     dcc.Input(id='pb_atma', type='number', value=130),

#     html.Label("T Res (C):"),
#     dcc.Input(id='t_res_C', type='number', value=80),

#     html.Label("BOB (m3/m3):"),
#     dcc.Input(id='bob_m3m3', type='number', value=1.2),

#     html.Label("MuOB (cP):"),
#     dcc.Input(id='muob_cP', type='number', value=0.6),

#     html.Label("PVT Correction Set:"),
#     dcc.Input(id='PVT_corr_set', type='number', value=0),

#     html.Label("Q Liq (sm3/day):"),
#     dcc.Input(id='q_liq_sm3day', type='number', value=50),

#     html.Label("FW Perc:"),
#     dcc.Input(id='fw_perc', type='number', value=0),

#     html.Label("RP (m3/m3):"),
#     dcc.Input(id='rp_m3m3', type='number', value=0),

#     html.Label("Q Gas Free (sm3/day):"),
#     dcc.Input(id='q_gas_free_sm3day', type='number', value=0),

#     html.Label("ESP Q Nom (sm3/day):"),
#     dcc.Input(id='ESP_q_nom', type='number', value=120),

#     html.Label("ESP Head Nom (m):"),
#     dcc.Input(id='ESP_head_nom', type='number', value=2000),

#     html.Label("Frequency Nom (Hz):"),
#     dcc.Input(id='freq_nom', type='number', value=48.5),

#     html.Label("Number of Stages:"),
#     dcc.Input(id='num_stages', type='number', value=10),

#     html.Label("Calibr Head:"),
#     dcc.Input(id='calibr_head', type='number', value=1),

#     html.Label("Calibr Rate:"),
#     dcc.Input(id='calibr_rate', type='number', value=1),

#     html.Label("Calibr Power:"),
#     dcc.Input(id='calibr_power', type='number', value=1),

#     html.Label("Gas Correct Model:"),
#     dcc.Input(id='gas_correct_model', type='number', value=1),

#     html.Label("Gas Correct Stage by Stage:"),
#     dcc.Input(id='gas_correct_stage_by_stage', type='number', value=0),

#     html.Label("Dnum Stages Integrate:"),
#     dcc.Input(id='dnum_stages_integrate', type='number', value=1),

#     html.Label("P Calc (Atm):"),
#     dcc.Input(id='p_calc_atma', type='number', value=150),

#     html.Label("T Intake (C):"),
#     dcc.Input(id='t_intake_C', type='number', value=80),

#     html.Label("T Dis (C):"),
#     dcc.Input(id='t_dis_C', type='number', value=80),

#     html.Label("Frequency (Hz):"),
#     dcc.Input(id='freq_Hz', type='number', value=50),

#     html.Label("Calc Along Flow:"),
#     dcc.Input(id='calc_along_flow', type='number', value=1),

#     html.Label("Param:"),
#     dcc.Input(id='param', type='number', value=1),

#     html.Label("H Mes Top:"),
#     dcc.Input(id='h_mes_top', type='number', value=2000),

#     html.Button('Calculate', id='calculate-button', n_clicks=0),
#     # html.Button('Stop Server', id='stop-button', n_clicks=0),

#     html.Div(id='output-data-upload'),
# ])


# # Функция обработки нажатия кнопки "Calculate"
# @app.callback(
#     Output('output-data-upload', 'children'),
#     [Input('calculate-button', 'n_clicks')],
#     [State('gamma_gas', 'value'),
#      State('gamma_oil', 'value'),
#      State('gamma_wat', 'value'),
#      State('rsb_m3m3', 'value'),
#      State('pb_atma', 'value'),
#      State('t_res_C', 'value'),
#      State('bob_m3m3', 'value'),
#      State('muob_cP', 'value'),
#      State('PVT_corr_set', 'value'),
#      State('q_liq_sm3day', 'value'),
#      State('fw_perc', 'value'),
#      State('rp_m3m3', 'value'),
#      State('q_gas_free_sm3day', 'value'),
#      State('ESP_q_nom', 'value'),
#      State('ESP_head_nom', 'value'),
#      State('freq_nom', 'value'),
#      State('num_stages', 'value'),
#      State('calibr_head', 'value'),
#      State('calibr_rate', 'value'),
#      State('calibr_power', 'value'),
#      State('gas_correct_model', 'value'),
#      State('gas_correct_stage_by_stage', 'value'),
#      State('dnum_stages_integrate', 'value'),
#      State('p_calc_atma', 'value'),
#      State('t_intake_C', 'value'),
#      State('t_dis_C', 'value'),
#      State('freq_Hz', 'value'),
#      State('calc_along_flow', 'value'),
#      State('param', 'value'),
#      State('h_mes_top', 'value')],
# )

# def update_output(n_clicks, gamma_gas, gamma_oil, gamma_wat, rsb_m3m3,
#                   pb_atma, t_res_C, bob_m3m3, muob_cP, PVT_corr_set, q_liq_sm3day, 
#                   fw_perc, rp_m3m3, q_gas_free_sm3day, ESP_q_nom, ESP_head_nom, freq_nom, 
#                   num_stages, calibr_head, calibr_rate, calibr_power, gas_correct_model, 
#                   gas_correct_stage_by_stage, dnum_stages_integrate, p_calc_atma, t_intake_C, 
#                   t_dis_C, freq_Hz, calc_along_flow, param, h_mes_top):
    
#     gor_values_pipesim_dif_gor = list(range(50, 500, 50))
#     liquid_flow_rates_pipesim_dif_gor = list(range(5, 300, 20))
#     gor_values_unifloc_dif_gor = gor_values_pipesim_dif_gor.copy()
#     liquid_flow_rates_unifloc_dif_gor = liquid_flow_rates_pipesim_dif_gor.copy()

#     if n_clicks > 0:
#         if 'unifloc_modeling_P_dis_OIL_dif_GOR_status':  # Убедитесь, что это условие выполняется
#             gor_Pdis_Q_unifloc = defaultdict(dict)

#             print("ESP_q_nom", ESP_q_nom)

#             # # Создание и использование PVT_ESP, feed_esp и вычисление p_dis
#             # esp = unf.encode_ESP_pump(
#             #     q_nom_sm3day=ESP_q_nom,
#             #     head_nom_m=ESP_head_nom,
#             #     freq_nom_Hz=freq_nom,
#             #     num_stages=num_stages,
#             #     calibr_head=calibr_head,
#             #     calibr_rate=calibr_rate,
#             #     calibr_power=calibr_power,
#             #     gas_correct_model=gas_correct_model,
#             #     gas_correct_stage_by_stage=gas_correct_stage_by_stage,
#             #     dnum_stages_integrate=dnum_stages_integrate
#             # )   

#             model = Model.open(PIPESIM_MODEL_PATH_ESP_P_DIS_OIL_BASE, Units.METRIC)
#             model.close()

#             # Encode ESP pump
#             esp = unf.encode_ESP_pump(
#                 q_nom_sm3day=ESP_q_nom_value,
#                 head_nom_m=ESP_head_nom_value,
#                 freq_nom_Hz=freq_nom_value,
#                 num_stages=num_stages_value,
#                 calibr_head=calibr_head_value,
#                 calibr_rate=calibr_rate_value,
#                 calibr_power=calibr_power_value,
#                 gas_correct_model=gas_correct_model_value,
#                 gas_correct_stage_by_stage=gas_correct_stage_by_stage_value,
#                 dnum_stages_integrate=dnum_stages_integrate_value
#             )

#             for gor_unifloc in gor_values_unifloc_dif_gor:
#                 p_dis_values_unifloc = []

#                 for q_liq_value in liquid_flow_rates_unifloc_dif_gor:

#                     print("qqq")

#                     PVT_ESP = unf.encode_PVT(
#                         gamma_gas=gamma_gas,
#                         gamma_oil=gamma_oil,
#                         gamma_wat=gamma_wat,
#                         rsb_m3m3=rsb_m3m3,
#                         pb_atma=pb_atma,
#                         t_res_C=t_res_C,
#                         bob_m3m3=bob_m3m3,
#                         muob_cP=muob_cP,
#                         PVT_corr_set=PVT_corr_set
#                     )
                    
#                     feed_esp = unf.encode_feed(
#                         q_liq_sm3day=q_liq_value,
#                         fw_perc=fw_perc,
#                         rp_m3m3=gor_unifloc,
#                         q_gas_free_sm3day=q_gas_free_sm3day,
#                         fluid=PVT_ESP
#                     )

#                     p_dis = unf.ESP_p_atma(
#                         p_calc_atma=p_calc_atma,
#                         t_intake_C=t_intake_C,
#                         t_dis_C=t_dis_C,
#                         feed=feed_esp,
#                         esp_json=esp,
#                         freq_Hz=freq_Hz,
#                         calc_along_flow=calc_along_flow,
#                         param=param,
#                         h_mes_top=h_mes_top
#                     )
                    
#                     p_dis_values_unifloc.append(p_dis)

#                 gor_Pdis_Q_unifloc[gor_unifloc][pressure_key_atma] = p_dis_values_unifloc
#                 gor_Pdis_Q_unifloc[gor_unifloc][liquid_flowrate_key_sm3_day] = liquid_flow_rates_unifloc

#             results_data[resuts_key_p_dis_unifloc_dif_gor][results_key_unifloc][p_dis_oil_key] = gor_Pdis_Q_unifloc
            
#             with open(os.path.join(results_directory, "Results_DASH.json"), 'w') as json_file:
#                 json.dump(results_data, json_file, indent=3)

#             return f"Результаты расчета давления на выходе ЭЦН сохранены в '{results_file_path}'."
#         else:
#             return "Моделирование не активно."
#     return "Пожалуйста, нажмите кнопку 'Calculate' для выполнения расчета."

# # # Функция обработки нажатия кнопки "Stop Server"
# # @app.callback(
# #     Output('output-data-upload', 'children'),
# #     [Input('stop-button', 'n_clicks')]
# # )

# # def stop_server(n_clicks):
# #     if n_clicks > 0:
# #         func = request.environ.get('werkzeug.server.shutdown')
# #         if func is None:
# #             raise RuntimeError('Not running with the Werkzeug Server')
# #         func()
# #         return "Сервер остановлен."

# # # Запуск приложения
# # if __name__ == '__main__':
# app.run_server(debug=True)