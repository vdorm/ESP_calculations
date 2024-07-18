
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

pipesim_modeling_FA_status = True # проводим ли расчет модели PIPESIM в рамках анализа свойств (Fluid Analysis - FA) или нет
unifloc_modeling_FA_status = True # проводим ли расчет модели Unifloc в рамках FA или нет

results_data = defaultdict(lambda: defaultdict(dict)) # создаем многоуровневый словарь для хранения результатов расчета

resuts_key_fluid_analysis = "Fluid_Analysis" # Ключ для расчетных значений в рамках FA

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

empty_key = "Empty"
empty_value = "Empty"


# ----------------------------------------------------------------------------------
# Моделирование в PIPESIM / Modeling in PIPESIM
# ----------------------------------------------------------------------------------

if pipesim_modeling_FA_status == True:
    print("--"*40)
    print("Комментарии ниже относятся расчетной части PIPESIM.")
    
    # Open the model
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
    # print(results-profile)

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
# Моделирование в Unifloc VBA / Modeling in Unifloc VBA
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
    
with open(results_file_path, "w") as json_file:
    json.dump(results_data, json_file, indent=3)

