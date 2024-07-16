import os
import pandas as pd
from sixgill.pipesim import Model
from sixgill.definitions import ModelComponents, Parameters, Constants, Units, NAN, ProfileVariables


def model_creation():
    current_directory = os.getcwd()
    pipesim_fluid_properties_model_name = "ESP_P_DIS_oil.pips"
    # MODEL_PATH = current_directory + "\\" + pipesim_fluid_properties_model_name
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), pipesim_fluid_properties_model_name)  


    gamma_gas = 0.6
    gamma_water = 1.1
    density_oil_kg_m3 = 860
    fw_perc_value = 0
    rsb_m3m3 = 120
    pb_atma_value = 130
    pb_bara_value = pb_atma_value*1.01325
    t_res_C_value = 80
    bob_m3m3_value = 1.2
    muob_cP_value = 0.6

    well_name = "Well"
    well_ambient_temperature_C = 80

    black_oil_fluid_name = "Oil_ESP"

    casing_name = "Casing"
    casing_roughness_mm = 0.0254
    casing_wallthickness_mm = 14.1478
    casing_inner_diameter_mm = 190.7794
    casing_top_measured_depth_m = 0
    casing_length_m = 30

    tubing_name = "Tubing"
    tubing_roughness_mm = 0.0254
    tubing_wallthickness_mm = 6.8834
    tubing_inner_diameter_mm = 100.5332
    tubing_top_measured_depth_m = 0
    tubing_length_m = 25

    uvalue_heat_transfer_coefficient_J_s_C_m2 = 28.39132

    packer_name = "Packer"
    packer_measured_depth_m = 20

    completion_name = "Vert Comp 1"
    completion_measured_depth_m = 25.5
    completion_reservoir_pressure_bara = 150
    completion_reservoir_temperature_C = 80
    completion_reservoir_pressure_sm3_d_bar = 2000000


    print("Opening model '{}'".format(MODEL_PATH))
    model_fluid_properties = Model.new(MODEL_PATH, units=Units.METRIC, overwrite=True)
    model_fluid_properties.save()
    model_fluid_properties.close()
    model_fluid_properties = Model.open(MODEL_PATH, units=Units.METRIC)

    print("Adding a black oil fluid.")
    model_fluid_properties.add(ModelComponents.BLACKOILFLUID, black_oil_fluid_name, 
                            parameters = {
                                            Parameters.BlackOilFluid.GOR:rsb_m3m3, 
                                            Parameters.BlackOilFluid.USEGASRATIO: Parameters.BlackOilFluid.GOR,
                                            Parameters.BlackOilFluid.GASSPECIFICGRAVITY: gamma_gas,
                                            Parameters.BlackOilFluid.WATERSPECIFICGRAVITY: gamma_water,
                                            Parameters.BlackOilFluid.WATERCUT:fw_perc_value,
                                            Parameters.BlackOilFluid.USEDEADOILDENSITY: True,
                                            Parameters.BlackOilFluid.DEADOILDENSITY: density_oil_kg_m3,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BUBBLEPOINTSATGAS_VALUE: rsb_m3m3,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BUBBLEPOINTSATGAS_PRESSURE: pb_bara_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BUBBLEPOINTSATGAS_TEMPERATURE: t_res_C_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.SOLUTIONGAS: Constants.BlackOilCalibrationSolutionGas.STANDING,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPOFVF_PRESSURE: pb_bara_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPOFVF_TEMPERATURE: t_res_C_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPOFVF_VALUE: bob_m3m3_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.OILFVFCORRELATION: Constants.BlackOilCalibrationSolutionGas.STANDING,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPLIVEOILVISCOSITY_VALUE: muob_cP_value ,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPLIVEOILVISCOSITY_PRESSURE: pb_bara_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.BELOWBBPLIVEOILVISCOSITY_TEMPERATURE: t_res_C_value,
                                            Parameters.BlackOilFluid.SinglePointCalibration.LIVEOILVISCCORRELATION: Constants.LiveOilViscCorrelation.BEGGSANDROBINSON,
                                            Parameters.BlackOilFluid.LIVEOILVISCOSITYCORR: Constants.LiveOilViscCorrelation.BEGGSANDROBINSON,
                                            })

    sim_srttings_luid_properties_model = model_fluid_properties.sim_settings
    sim_srttings_luid_properties_model['SingleBranchKeywords'] = 'HEAT BALANCE = OFF'

    model_fluid_properties.add(ModelComponents.WELL, well_name,
                                parameters={Parameters.Well.DeviationSurvey.SURVEYTYPE: Constants.DeviationSurveyType.TWODIMENSIONAL,
                                            Parameters.Well.DeviationSurvey.DEPENDENTPARAMETER: Constants.TrajectoryDependentParameter.ANGLE,
                                            Parameters.Well.DeviationSurvey.CALCULATEUSINGTANGENTIALMETHOD: True,
                                            Parameters.Well.ASSOCIATEDBLACKOILFLUID: black_oil_fluid_name,
                                            Parameters.Well.HeatTransfer.UVALUEINPUTOPTION: Constants.UValueInputOption.InputSingleUValue,
                                            Parameters.Well.HeatTransfer.UCOEFF: uvalue_heat_transfer_coefficient_J_s_C_m2,
                                            Parameters.Well.AMBIENTTEMPERATURE: well_ambient_temperature_C,
                                            # Parameters.Well.HeatTransfer.
                                            })

    print(f"Setting the tubing and casing for Well '{well_name}'.")
    model_fluid_properties.add(ModelComponents.TUBING, tubing_name, context=well_name,
                                parameters={Parameters.Tubing.TOPMEASUREDDEPTH: tubing_top_measured_depth_m,
                                            Parameters.Tubing.LENGTH: tubing_length_m,
                                            Parameters.Tubing.INNERDIAMETER: tubing_inner_diameter_mm,
                                            Parameters.Tubing.ROUGHNESS: tubing_roughness_mm,
                                            Parameters.Tubing.WALLTHICKNESS: tubing_wallthickness_mm})

    model_fluid_properties.add(ModelComponents.CASING, casing_name, context=well_name,
                                parameters={Parameters.Casing.TOPMEASUREDDEPTH: casing_top_measured_depth_m,
                                            Parameters.Casing.LENGTH: casing_length_m,
                                            Parameters.Casing.INNERDIAMETER: casing_inner_diameter_mm,
                                            Parameters.Casing.ROUGHNESS: casing_roughness_mm,
                                            Parameters.Casing.WALLTHICKNESS: casing_wallthickness_mm})

    model_fluid_properties.add(ModelComponents.PACKER, packer_name, 
                                context=well_name, 
                                parameters={Parameters.Packer.TOPMEASUREDDEPTH:packer_measured_depth_m})

    model_fluid_properties.add(ModelComponents.COMPLETION, completion_name, context=well_name,
                                parameters={Parameters.Completion.TOPMEASUREDDEPTH: completion_measured_depth_m,
                                            Parameters.Completion.FLUIDENTRYTYPE: Constants.CompletionFluidEntry.SINGLEPOINT,
                                            Parameters.Completion.GEOMETRYPROFILETYPE: Constants.Orientation.VERTICAL,
                                            Parameters.Completion.IPRMODEL: Constants.IPRModels.IPRPIMODEL,
                                            Parameters.Completion.RESERVOIRPRESSURE: completion_reservoir_pressure_bara,
                                            Parameters.IPRPIModel.LIQUIDPI: completion_reservoir_pressure_sm3_d_bar,
                                            Parameters.IPRPIModel.USEVOGELBELOWBUBBLEPOINT: True,
                                            Parameters.Completion.RESERVOIRTEMPERATURE: completion_reservoir_temperature_C,
                                            Parameters.Well.ASSOCIATEDBLACKOILFLUID: black_oil_fluid_name,
                                        })

    print(f"Adding an ESP to Well '{well_name}'.")
    model_fluid_properties.add(ModelComponents.ESP, "Esp1", context=well_name, \
                                parameters={Parameters.ESP.TOPMEASUREDDEPTH:25,
                                            Parameters.ESP.OPERATINGFREQUENCY:50,
                                            Parameters.ESP.MANUFACTURER:"Unifloc",
                                            Parameters.ESP.MODEL:"737",
                                            Parameters.ESP.NUMBERSTAGES:10,
                                            Parameters.ESP.HEADFACTOR:1,
                                            Parameters.ESP.POWERFACTOR:1,
                                            Parameters.ESP.USEVISCOSITYCORRECTION:False})

    model_fluid_properties.set_value("Esp1", value=10, parameter=Parameters.ESP.NUMBERSTAGES)

    # Create the new trajectory dataframe
    new_trajectory = {}
    new_trajectory[Parameters.WellTrajectory.TRUEVERTICALDEPTH] = [0.0, 10.0, 25.0]
    new_trajectory[Parameters.WellTrajectory.MEASUREDDEPTH] = [0.0, 10.0, 25.0]
    df_trajectory = pd.DataFrame(new_trajectory)

    print("Setting new well trajectory")
    model_fluid_properties.set_trajectory(context=well_name, value=df_trajectory)

    profile_variables = [
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.VISCOSITY_OIL_INSITU, 
        ProfileVariables.SOLUTION_GAS_IN_OIL_INSITU,
        ProfileVariables.FORMATION_VOLUME_FACTOR_OIL_INSITU,
        ProfileVariables.DENSITY_OIL_INSITU,
    ]

    parameters = {
        Parameters.PTProfileSimulation.INLETPRESSURE: 151.9875,
        Parameters.PTProfileSimulation.LIQUIDFLOWRATE: 5,
        Parameters.PTProfileSimulation.FLOWRATETYPE: Constants.FlowRateType.LIQUIDFLOWRATE,
        Parameters.PTProfileSimulation.CALCULATEDVARIABLE: Constants.CalculatedVariable.OUTLETPRESSURE,
    }

    results = model_fluid_properties.tasks.ptprofilesimulation.run(
                producer=well_name,
                parameters=parameters,
                profile_variables=profile_variables, 
    )

    print("Simulation state = {}".format(results.state))

    # profile results
    for case, profile in results.profile.items():
        print ("\nProfile result for {}".format(case))
        profile_df = pd.DataFrame.from_dict(profile)
        print (profile_df)

    print("All finished. Saving model...")
    model_fluid_properties.save()
    model_fluid_properties.close()

if __name__ == "__main__":
    model_creation()