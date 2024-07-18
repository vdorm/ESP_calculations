
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
pipesim_modeling_P_dis_OIL_status = False # проводим ли расчет модели PIPESIM в рамках анализа работы ЭЦН (флюид: нефть - ESP_O) или нет
unifloc_modeling_P_dis_OIL_status = True # проводим ли расчет модели Unifloc в рамках анализа ESP_O или нет

results_data = defaultdict(lambda: defaultdict(dict)) # создаем многоуровневый словарь для хранения результатов расчета

resuts_key_fluid_analysis = "Fluid_Analysis" # Ключ для расчетных значений в рамках FA
resuts_key_p_dis_water = "P_dis_water_case" # Ключ для расчетных значений в рамках анализа расчета перепада давления, создаваемым ЭЦН, при прокачке воды
resuts_key_p_dis_oil = "P_dis_oil_case" # Ключ для расчетных значений в рамках анализа расчета перепада давления, создаваемым ЭЦН, при прокачке ГЖС

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
# Моделирование расчета Discharge Pressure в PIPESIM / 
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

with open(results_file_path, "w") as json_file:
    json.dump(results_data, json_file, indent=3)

