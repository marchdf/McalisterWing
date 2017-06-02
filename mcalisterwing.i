Simulations:
  - name: sim1
    time_integrator: ti_1
    optimizer: opt1

linear_solvers:

  - name: solve_scalar
    type: tpetra
    method: gmres
    preconditioner: sgs
    tolerance: 1e-5
    max_iterations: 50
    kspace: 50
    output_level: 0

  - name: solve_cont
    type: tpetra
    method: gmres
    preconditioner: muelu
    tolerance: 1e-5
    max_iterations: 50
    kspace: 50
    output_level: 0

realms:

  - name: realm_1
    mesh: grid07_conformal01.exo
    use_edges: yes
    check_for_missing_bcs: yes
    automatic_decomposition_type: rcb

    time_step_control:
     target_courant: 10.0
     time_step_change_factor: 1.2

    equation_systems:
      name: theEqSys
      max_iterations: 2 

      solver_system_specification:
        velocity: solve_scalar
        turbulent_ke: solve_scalar
        specific_dissipation_rate: solve_scalar
        pressure: solve_cont

      systems:

        - LowMachEOM:
            name: myLowMach
            max_iterations: 1
            convergence_tolerance: 1e-5

        - ShearStressTransport:
            name: mySST 
            max_iterations: 1
            convergence_tolerance: 1e-5

    initial_conditions:
      - constant: ic_1
        target_name: [Upstream-HEX,TipVortex-HEX,WingBox-HEX,WingBox-WEDGE,TestSection-PYRAMID,WingBox-PYRAMID,TestSection-TETRA,WingBox-TETRA]
        value:
          pressure: 0
          velocity: [46,0.0,0.0]
          turbulent_ke: 0.001127
          specific_dissipation_rate: 7983.14

    material_properties:
      target_name: [Upstream-HEX,TipVortex-HEX,WingBox-HEX,WingBox-WEDGE,TestSection-PYRAMID,WingBox-PYRAMID,TestSection-TETRA,WingBox-TETRA]
      specifications:
        - name: density
          type: constant
          value: 1.177
        - name: viscosity
          type: constant
          value: 1.846e-5

    boundary_conditions:

    - wall_boundary_condition: bc_wall
      target_name: Support
      wall_user_data:
        velocity: [0,0,0]
        turbulent_ke: 0.0
        use_wall_function: no

    - wall_boundary_condition: bc_wall
      target_name: TunnelWalls
      wall_user_data:
        velocity: [0,0,0]
        turbulent_ke: 0.0
        use_wall_function: no

    - wall_boundary_condition: bc_wall
      target_name: Wing
      wall_user_data:
        velocity: [0,0,0]
        turbulent_ke: 0.0
        use_wall_function: no

    - inflow_boundary_condition: bc_inflow
      target_name: TunnelInlet
      inflow_user_data:
        velocity: [46,0.0,0.0]
        turbulent_ke: 0.001127
        specific_dissipation_rate: 7983.14

    - open_boundary_condition: bc_open
      target_name: TunnelOutlet
      open_user_data:
        velocity: [0,0,0]
        pressure: 0.0
        turbulent_ke: 0.001127
        specific_dissipation_rate: 7983.14

    solution_options:
      name: myOptions
      turbulence_model: sst_des

      options:
        - hybrid_factor:
            velocity: 1.0 
            turbulent_ke: 1.0
            specific_dissipation_rate: 1.0

        - alpha_upw:
            velocity: 1.0 

        - limiter:
            pressure: no
            velocity: yes
            turbulent_ke: yes
            specific_dissipation_rate: yes

        - projected_nodal_gradient:
            velocity: element
            pressure: element 
            turbulent_ke: element
            specific_dissipation_rate: element
    
        - input_variables_from_file:
            minimum_distance_to_wall: ndtw

        - turbulence_model_constants:
            SDRWallFactor: 10.0

    data_probes:

      output_frequency: 500

      search_method: stk_octree
      search_tolerance: 1.0e-3
      search_expansion_factor: 2.0

      specifications:
        - name: probe_vortex
          from_target_part: TipVortex-HEX

          line_of_site_specifications:
            - name: results/probe_0
              number_of_points: 100
              tip_coordinates: [0.0, 0.0, 0.0 ]
              tail_coordinates: [30.0, 0.0, 0.0]

            - name: results/probe_1
              number_of_points: 400
              tip_coordinates: [-110.0, 0.0, 1.0 ]
              tail_coordinates: [0.0, 0.0, 1.0]

          output_variables:
            - field_name: velocity
              field_size: 3
            - field_name: pressure
              field_size: 1

    post_processing:

    - type: surface
      physics: surface_force_and_moment
      output_file_name: results/McalisterWing.dat
      frequency: 1000
      parameters: [0,0]
      target_name: Wing

    output:
      output_data_base_name: results/McalisterWing.e
      output_frequency: 1000
      output_node_set: no
      output_variables:
       - velocity
       - pressure
       - pressure_force
       - tau_wall
       - turbulent_ke
       - specific_dissipation_rate
       - minimum_distance_to_wall
       - sst_f_one_blending
       - turbulent_viscosity

    restart:
      restart_data_base_name: restart/McalisterWing.rst
      output_frequency: 5000

Time_Integrators:
  - StandardTimeIntegrator:
      name: ti_1
      start_time: 0
      time_step: 1.0e-10
      termination_time: 1
      time_stepping_type: adaptive
      time_step_count: 0

      realms: 
        - realm_1
