import numpy as np
import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute, transpile

from qiskit.transpiler import PassManager

from qiskit.converters import circuit_to_dag
from qiskit.visualization import dag_drawer, plot_histogram
from qiskit.compiler import assemble
from qiskit.tools.monitor import job_monitor

from qiskit import IBMQ

from qiskit.test.mock import FakeManhattan
from qiskit.test.mock import FakeMumbai
from qiskit.test.mock import FakeTokyo


"""
Pass manager for optimization level 3 including trios, providing heavy optimization.

Level 3 pass manager: heavy optimization by noise adaptive qubit mapping and
gate cancellation using commutativity rules and unitary synthesis.
"""

#import all original libraries
from qiskit.transpiler.passmanager_config import PassManagerConfig
from qiskit.transpiler.timing_constraints import TimingConstraints
from qiskit.transpiler.passmanager import PassManager

from qiskit.transpiler.passes import Unroller
from qiskit.transpiler.passes import BasisTranslator
from qiskit.transpiler.passes import UnrollCustomDefinitions
from qiskit.transpiler.passes import Unroll3qOrMore
from qiskit.transpiler.passes import CheckMap
from qiskit.transpiler.passes import GateDirection
from qiskit.transpiler.passes import SetLayout
from qiskit.transpiler.passes import CSPLayout
from qiskit.transpiler.passes import TrivialLayout
from qiskit.transpiler.passes import DenseLayout
from qiskit.transpiler.passes import NoiseAdaptiveLayout
from qiskit.transpiler.passes import SabreLayout
from qiskit.transpiler.passes import BarrierBeforeFinalMeasurements
from qiskit.transpiler.passes import BasicSwap
from qiskit.transpiler.passes import LookaheadSwap
from qiskit.transpiler.passes import StochasticSwap
from qiskit.transpiler.passes import SabreSwap
from qiskit.transpiler.passes import FullAncillaAllocation
from qiskit.transpiler.passes import EnlargeWithAncilla
from qiskit.transpiler.passes import FixedPoint
from qiskit.transpiler.passes import Depth
from qiskit.transpiler.passes import RemoveResetInZeroState
from qiskit.transpiler.passes import Optimize1qGatesDecomposition
from qiskit.transpiler.passes import CommutativeCancellation
from qiskit.transpiler.passes import OptimizeSwapBeforeMeasure
from qiskit.transpiler.passes import RemoveDiagonalGatesBeforeMeasure
from qiskit.transpiler.passes import Collect2qBlocks
from qiskit.transpiler.passes import ConsolidateBlocks
from qiskit.transpiler.passes import UnitarySynthesis
from qiskit.transpiler.passes import ApplyLayout
from qiskit.transpiler.passes import Layout2qDistance
from qiskit.transpiler.passes import CheckGateDirection
from qiskit.transpiler.passes import TimeUnitConversion
from qiskit.transpiler.passes import ALAPSchedule
from qiskit.transpiler.passes import ASAPSchedule
from qiskit.transpiler.passes import AlignMeasures
from qiskit.transpiler.passes import ValidatePulseGates
from qiskit.transpiler.passes import Error

from qiskit.transpiler import TranspilerError

#importing all edited libraries
from unroll_3q_or_more_ import Unroll3qOrMore_
from remove_reset_in_zero_state_ import RemoveResetInZeroState_
from remove_diagonal_gates_before_measure_ import RemoveDiagonalGatesBeforeMeasure_
from set_layout_ import SetLayout_
from trivial_layout_ import TrivialLayout_
from layout_2qplus_distance_ import Layout2qPlusDistance_
from csp_layout_ import CSPLayout_
from dense_layout_ import DenseLayout_
from noise_adaptive_layout_ import NoiseAdaptiveLayout_
from full_ancilla_allocation_ import FullAncillaAllocation_
from enlarge_with_ancilla_ import EnlargeWithAncilla_
from apply_layout_ import ApplyLayout_
from check_map_ import CheckMap_
from barrier_before_final_measurements_ import BarrierBeforeFinalMeasurements_
from basic_swap_ import BasicSwap_
from unroll_toffoli_ import UnrollToffoli_
from context_aware_decompose_ import UnrollToffoliContextAware_, UnrollCnotContextAware_

from typing import List, Union, Dict, Callable, Any, Optional, Tuple

from qiskit.dagcircuit import DAGCircuit
from qiskit.providers import BaseBackend
from qiskit.providers.backend import Backend
from qiskit.providers.models import BackendProperties
from qiskit.providers.models.backendproperties import Gate
from qiskit.pulse import Schedule
from qiskit.tools.parallel import parallel_map
from qiskit.transpiler import Layout, CouplingMap, PropertySet, PassManager
from qiskit.transpiler.basepasses import BasePass
from qiskit.transpiler.exceptions import TranspilerError
from qiskit.transpiler.instruction_durations import InstructionDurations, InstructionDurationsType
from qiskit.transpiler.passes import ApplyLayout
from qiskit.transpiler.passmanager_config import PassManagerConfig
from qiskit.transpiler.timing_constraints import TimingConstraints

import qiskit
import qiskit_superstaq



def level_3_context_pulse_pass_manager(pass_manager_config: PassManagerConfig) -> PassManager:
    """Level 3 pass manager: heavy optimization by noise adaptive qubit mapping and
    gate cancellation using commutativity rules and unitary synthesis.

    This pass manager applies the user-given initial layout. If none is given, a search
    for a perfect layout (i.e. one that satisfies all 2-qubit interactions) is conducted.
    If no such layout is found, and device calibration information is available, the
    circuit is mapped to the qubits with best readouts and to CX gates with highest fidelity.

    The pass manager then transforms the circuit to match the coupling constraints.
    It is then unrolled to the basis, and any flipped cx directions are fixed.
    Finally, optimizations in the form of commutative gate cancellation, resynthesis
    of two-qubit unitary blocks, and redundant reset removal are performed.

    Note:
        In simulators where ``coupling_map=None``, only the unrolling and
        optimization stages are done.

    Args:
        pass_manager_config: configuration of the pass manager.

    Returns:
        a level 3 pass manager.

    Raises:
        TranspilerError: if the passmanager config is invalid.
    """
    basis_gates = pass_manager_config.basis_gates
    coupling_map = pass_manager_config.coupling_map
    orientation_map = pass_manager_config.orientation_map
    initial_layout = pass_manager_config.initial_layout
    
    
    layout_method = pass_manager_config.layout_method or "dense" #works for all cases other than sabre
    print('layout_method: ', layout_method)
    
    #enforcing the basic swap policy at all times
    routing_method = pass_manager_config.routing_method or "basic" #works only for basic
    print('routing method: ', routing_method)
    
    translation_method = pass_manager_config.translation_method or "translator"
    scheduling_method = pass_manager_config.scheduling_method
    instruction_durations = pass_manager_config.instruction_durations
    seed_transpiler = pass_manager_config.seed_transpiler
    backend_properties = pass_manager_config.backend_properties
    approximation_degree = pass_manager_config.approximation_degree
    timing_constraints = pass_manager_config.timing_constraints or TimingConstraints()

    # 1. Unroll to 1q or 2q gates
    _unroll3q = Unroll3qOrMore_()

    # 2. Layout on good qubits if calibration info available, otherwise on dense links
    _given_layout = SetLayout_(initial_layout)

    def _choose_layout_condition(property_set):
        # layout hasn't been set yet
        return not property_set["layout"]

    def _csp_not_found_match(property_set):
        # If a layout hasn't been set by the time we run csp we need to run layout
        if property_set["layout"] is None:
            return True
        # if CSP layout stopped for any reason other than solution found we need
        # to run layout since CSP didn't converge.
        if (
            property_set["CSPLayout_stop_reason"] is not None
            and property_set["CSPLayout_stop_reason"] != "solution found"
        ):
            return True
        return False

    # 2a. If layout method is not set, first try a trivial layout
    _choose_layout_0 = (
        []
        if pass_manager_config.layout_method
        else [
            TrivialLayout_(coupling_map),
            Layout2qPlusDistance_(coupling_map, property_name="trivial_layout_score"),
        ]
    )
    # 2b. If trivial layout wasn't perfect (ie no swaps are needed) then try
    # using CSP layout to find a perfect layout
    _choose_layout_1 = (
        []
        if pass_manager_config.layout_method
        else CSPLayout_(coupling_map, call_limit=10000, time_limit=60, seed=seed_transpiler)
    )

    def _trivial_not_perfect(property_set):
        # Verify that a trivial layout  is perfect. If trivial_layout_score > 0
        # the layout is not perfect. The layout property set is unconditionally
        # set by trivial layout so we clear that before running CSP
        if property_set["trivial_layout_score"] is not None:
            if property_set["trivial_layout_score"] != 0:
                #property_set["layout"]._wrapped = None
                return True
        return False

    # 2c. if CSP didn't converge on a solution use layout_method (dense).
    if layout_method == "trivial":
        _choose_layout_2 = TrivialLayout_(coupling_map)
    elif layout_method == "dense":
        _choose_layout_2 = DenseLayout_(coupling_map, backend_properties)
    elif layout_method == "noise_adaptive":
        _choose_layout_2 = NoiseAdaptiveLayout_(backend_properties)
    elif layout_method == "sabre":
        _choose_layout_2 = SabreLayout(coupling_map, max_iterations=4, seed=seed_transpiler)
    else:
        raise TranspilerError("Invalid layout method %s." % layout_method)

    # 3. Extend dag/layout with ancillas using the full coupling map
    _embed = [FullAncillaAllocation_(coupling_map), EnlargeWithAncilla_(), ApplyLayout_()]

    # 4. Swap to fit the coupling map
    _swap_check = CheckMap_(coupling_map)

    def _swap_condition(property_set):
        return not property_set["is_swap_mapped"]

    _swap = [BarrierBeforeFinalMeasurements_()]
    if routing_method == "basic":
        _swap += [BasicSwap_(coupling_map)]
    elif routing_method == "stochastic":
        _swap += [StochasticSwap(coupling_map, trials=200, seed=seed_transpiler)]
    elif routing_method == "lookahead":
        _swap += [LookaheadSwap(coupling_map, search_depth=5, search_width=6)]
    elif routing_method == "sabre":
        _swap += [SabreSwap(coupling_map, heuristic="decay", seed=seed_transpiler)]
    elif routing_method == "none":
        _swap += [
            Error(
                msg="No routing method selected, but circuit is not routed to device. "
                "CheckMap Error: {check_map_msg}",
                action="raise",
            )
        ]
    else:
        raise TranspilerError("Invalid routing method %s." % routing_method)
    
    #unroll gates in a context-aware way
    _unroll_context = [UnrollToffoliContextAware_(coupling_map)]

    # 5. Unroll to the basis
    if translation_method == "unroller":
        _unroll = [Unroller(basis_gates)]
    elif translation_method == "translator":
        from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

        _unroll = [UnrollCustomDefinitions(sel, basis_gates), BasisTranslator(sel, basis_gates)]
    elif translation_method == "synthesis":
        _unroll = [
            Unroll3qOrMore(),
            Collect2qBlocks(),
            ConsolidateBlocks(basis_gates=basis_gates),
            UnitarySynthesis(
                basis_gates,
                approximation_degree=approximation_degree,
                coupling_map=coupling_map,
                backend_props=backend_properties,
            ),
        ]
    else:
        raise TranspilerError("Invalid translation method %s." % translation_method)

    # 6. Fix any CX direction mismatch
    _direction_check = [CheckGateDirection(coupling_map)]

    def _direction_condition(property_set):
        return not property_set["is_direction_mapped"]

    _direction = [GateDirection(coupling_map)]

    # 8. Optimize iteratively until no more change in depth. Removes useless gates
    # after reset and before measure, commutes gates and optimizes contiguous blocks.
    _depth_check = [Depth(), FixedPoint("depth")]

    def _opt_control(property_set):
        return not property_set["depth_fixed_point"]

    _reset = [RemoveResetInZeroState()]

    _meas = [OptimizeSwapBeforeMeasure(), RemoveDiagonalGatesBeforeMeasure()]

    _opt = [
        Collect2qBlocks(),
        ConsolidateBlocks(basis_gates=basis_gates),
        UnitarySynthesis(
            basis_gates,
            approximation_degree=approximation_degree,
            coupling_map=coupling_map,
            backend_props=backend_properties,
        ),
        Optimize1qGatesDecomposition(basis_gates),
        CommutativeCancellation(),
    ]

    # 9. Unify all durations (either SI, or convert to dt if known)
    # Schedule the circuit only when scheduling_method is supplied
    _scheduling = [TimeUnitConversion(instruction_durations)]
    if scheduling_method:
        if scheduling_method in {"alap", "as_late_as_possible"}:
            _scheduling += [ALAPSchedule(instruction_durations)]
        elif scheduling_method in {"asap", "as_soon_as_possible"}:
            _scheduling += [ASAPSchedule(instruction_durations)]
        else:
            raise TranspilerError("Invalid scheduling method %s." % scheduling_method)

    # 10. Call measure alignment. Should come after scheduling.
    _alignments = [
        ValidatePulseGates(
            granularity=timing_constraints.granularity, min_length=timing_constraints.min_length
        ),
        AlignMeasures(alignment=timing_constraints.acquire_alignment),
    ]
    # 11. Unroll the CNOT gates with pulse-level awareness:
    _pulse_context = [UnrollCnotContextAware_(coupling_map, orientation_map)]

    # Build pass manager
    pm3 = PassManager()
    pm3.append(_unroll3q)
    pm3.append(_reset + _meas)
    if coupling_map or initial_layout:
        pm3.append(_given_layout)
        pm3.append(_choose_layout_0, condition=_choose_layout_condition)
        pm3.append(_choose_layout_1, condition=_trivial_not_perfect)
        pm3.append(_choose_layout_2, condition=_csp_not_found_match)
        pm3.append(_embed)
        pm3.append(_swap_check)
        pm3.append(_swap, condition=_swap_condition) #_swap performs routing. Only able to route 2 qubit and Toffoli gates.
    pm3.append([Collect2qBlocks()])
    pm3.append(_unroll_context) #the pass which performs the decompositions of the toffoli gate
    pm3.append(_unroll)
    if coupling_map and not coupling_map.is_symmetric:
        pm3.append(_direction_check)
        pm3.append(_direction, condition=_direction_condition)
    pm3.append(_reset)
    pm3.append(_depth_check + _opt + _unroll, do_while=_opt_control)
    pm3.append(_scheduling)
    pm3.append(_alignments)
    pm3.append(_pulse_context)

    return pm3

def level_3_pulse_pass_manager(pass_manager_config: PassManagerConfig) -> PassManager:
    """Level 3 pass manager: heavy optimization by noise adaptive qubit mapping and
    gate cancellation using commutativity rules and unitary synthesis.

    This pass manager applies the user-given initial layout. If none is given, a search
    for a perfect layout (i.e. one that satisfies all 2-qubit interactions) is conducted.
    If no such layout is found, and device calibration information is available, the
    circuit is mapped to the qubits with best readouts and to CX gates with highest fidelity.

    The pass manager then transforms the circuit to match the coupling constraints.
    It is then unrolled to the basis, and any flipped cx directions are fixed.
    Finally, optimizations in the form of commutative gate cancellation, resynthesis
    of two-qubit unitary blocks, and redundant reset removal are performed.

    Note:
        In simulators where ``coupling_map=None``, only the unrolling and
        optimization stages are done.

    Args:
        pass_manager_config: configuration of the pass manager.

    Returns:
        a level 3 pass manager.

    Raises:
        TranspilerError: if the passmanager config is invalid.
    """
    basis_gates = pass_manager_config.basis_gates
    coupling_map = pass_manager_config.coupling_map
    orientation_map = pass_manager_config.orientation_map
    initial_layout = pass_manager_config.initial_layout
    
    
    layout_method = pass_manager_config.layout_method or "dense" #works for all cases other than sabre
    print('layout_method: ', layout_method)
    
    #enforcing the basic swap policy at all times
    routing_method = pass_manager_config.routing_method or "basic" #works only for basic
    print('routing method: ', routing_method)
    
    translation_method = pass_manager_config.translation_method or "translator"
    scheduling_method = pass_manager_config.scheduling_method
    instruction_durations = pass_manager_config.instruction_durations
    seed_transpiler = pass_manager_config.seed_transpiler
    backend_properties = pass_manager_config.backend_properties
    approximation_degree = pass_manager_config.approximation_degree
    timing_constraints = pass_manager_config.timing_constraints or TimingConstraints()

    # 1. Unroll to 1q or 2q gates
    _unroll3q = Unroll3qOrMore_()

    # 2. Layout on good qubits if calibration info available, otherwise on dense links
    _given_layout = SetLayout_(initial_layout)

    def _choose_layout_condition(property_set):
        # layout hasn't been set yet
        return not property_set["layout"]

    def _csp_not_found_match(property_set):
        # If a layout hasn't been set by the time we run csp we need to run layout
        if property_set["layout"] is None:
            return True
        # if CSP layout stopped for any reason other than solution found we need
        # to run layout since CSP didn't converge.
        if (
            property_set["CSPLayout_stop_reason"] is not None
            and property_set["CSPLayout_stop_reason"] != "solution found"
        ):
            return True
        return False

    # 2a. If layout method is not set, first try a trivial layout
    _choose_layout_0 = (
        []
        if pass_manager_config.layout_method
        else [
            TrivialLayout_(coupling_map),
            Layout2qPlusDistance_(coupling_map, property_name="trivial_layout_score"),
        ]
    )
    # 2b. If trivial layout wasn't perfect (ie no swaps are needed) then try
    # using CSP layout to find a perfect layout
    _choose_layout_1 = (
        []
        if pass_manager_config.layout_method
        else CSPLayout_(coupling_map, call_limit=10000, time_limit=60, seed=seed_transpiler)
    )

    def _trivial_not_perfect(property_set):
        # Verify that a trivial layout  is perfect. If trivial_layout_score > 0
        # the layout is not perfect. The layout property set is unconditionally
        # set by trivial layout so we clear that before running CSP
        if property_set["trivial_layout_score"] is not None:
            if property_set["trivial_layout_score"] != 0:
                #property_set["layout"]._wrapped = None
                return True
        return False

    # 2c. if CSP didn't converge on a solution use layout_method (dense).
    if layout_method == "trivial":
        _choose_layout_2 = TrivialLayout_(coupling_map)
    elif layout_method == "dense":
        _choose_layout_2 = DenseLayout_(coupling_map, backend_properties)
    elif layout_method == "noise_adaptive":
        _choose_layout_2 = NoiseAdaptiveLayout_(backend_properties)
    elif layout_method == "sabre":
        _choose_layout_2 = SabreLayout(coupling_map, max_iterations=4, seed=seed_transpiler)
    else:
        raise TranspilerError("Invalid layout method %s." % layout_method)

    # 3. Extend dag/layout with ancillas using the full coupling map
    _embed = [FullAncillaAllocation_(coupling_map), EnlargeWithAncilla_(), ApplyLayout_()]

    # 4. Swap to fit the coupling map
    _swap_check = CheckMap_(coupling_map)

    def _swap_condition(property_set):
        return not property_set["is_swap_mapped"]

    _swap = [BarrierBeforeFinalMeasurements_()]
    if routing_method == "basic":
        _swap += [BasicSwap_(coupling_map)]
    elif routing_method == "stochastic":
        _swap += [StochasticSwap(coupling_map, trials=200, seed=seed_transpiler)]
    elif routing_method == "lookahead":
        _swap += [LookaheadSwap(coupling_map, search_depth=5, search_width=6)]
    elif routing_method == "sabre":
        _swap += [SabreSwap(coupling_map, heuristic="decay", seed=seed_transpiler)]
    elif routing_method == "none":
        _swap += [
            Error(
                msg="No routing method selected, but circuit is not routed to device. "
                "CheckMap Error: {check_map_msg}",
                action="raise",
            )
        ]
    else:
        raise TranspilerError("Invalid routing method %s." % routing_method)
    
    #unroll toffoli in a layout-aware way
    _unroll_toffoli = [UnrollToffoli_(coupling_map)]

    # 5. Unroll to the basis
    if translation_method == "unroller":
        _unroll = [Unroller(basis_gates)]
    elif translation_method == "translator":
        from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary as sel

        _unroll = [UnrollCustomDefinitions(sel, basis_gates), BasisTranslator(sel, basis_gates)]
    elif translation_method == "synthesis":
        _unroll = [
            Unroll3qOrMore(),
            Collect2qBlocks(),
            ConsolidateBlocks(basis_gates=basis_gates),
            UnitarySynthesis(
                basis_gates,
                approximation_degree=approximation_degree,
                coupling_map=coupling_map,
                backend_props=backend_properties,
            ),
        ]
    else:
        raise TranspilerError("Invalid translation method %s." % translation_method)

    # 6. Fix any CX direction mismatch
    _direction_check = [CheckGateDirection(coupling_map)]

    def _direction_condition(property_set):
        return not property_set["is_direction_mapped"]

    _direction = [GateDirection(coupling_map)]

    # 8. Optimize iteratively until no more change in depth. Removes useless gates
    # after reset and before measure, commutes gates and optimizes contiguous blocks.
    _depth_check = [Depth(), FixedPoint("depth")]

    def _opt_control(property_set):
        return not property_set["depth_fixed_point"]

    _reset = [RemoveResetInZeroState()]

    _meas = [OptimizeSwapBeforeMeasure(), RemoveDiagonalGatesBeforeMeasure()]

    _opt = [
        Collect2qBlocks(),
        ConsolidateBlocks(basis_gates=basis_gates),
        UnitarySynthesis(
            basis_gates,
            approximation_degree=approximation_degree,
            coupling_map=coupling_map,
            backend_props=backend_properties,
        ),
        Optimize1qGatesDecomposition(basis_gates),
        CommutativeCancellation(),
    ]

    # 9. Unify all durations (either SI, or convert to dt if known)
    # Schedule the circuit only when scheduling_method is supplied
    _scheduling = [TimeUnitConversion(instruction_durations)]
    if scheduling_method:
        if scheduling_method in {"alap", "as_late_as_possible"}:
            _scheduling += [ALAPSchedule(instruction_durations)]
        elif scheduling_method in {"asap", "as_soon_as_possible"}:
            _scheduling += [ASAPSchedule(instruction_durations)]
        else:
            raise TranspilerError("Invalid scheduling method %s." % scheduling_method)

    # 10. Call measure alignment. Should come after scheduling.
    _alignments = [
        ValidatePulseGates(
            granularity=timing_constraints.granularity, min_length=timing_constraints.min_length
        ),
        AlignMeasures(alignment=timing_constraints.acquire_alignment),
    ]
    # 11. Unroll the CNOT gates with pulse-level awareness:
    _pulse_context = [UnrollCnotContextAware_(coupling_map, orientation_map)]

    # Build pass manager
    pm3 = PassManager()
    pm3.append(_unroll3q)
    pm3.append(_reset + _meas)
    if coupling_map or initial_layout:
        pm3.append(_given_layout)
        pm3.append(_choose_layout_0, condition=_choose_layout_condition)
        pm3.append(_choose_layout_1, condition=_trivial_not_perfect)
        pm3.append(_choose_layout_2, condition=_csp_not_found_match)
        pm3.append(_embed)
        pm3.append(_swap_check)
        pm3.append(_swap, condition=_swap_condition) #_swap performs routing. Only able to route 2 qubit and Toffoli gates.
    pm3.append(_unroll_toffoli) #the pass which performs the decompositions of the toffoli gate
    pm3.append(_unroll)
    if coupling_map and not coupling_map.is_symmetric:
        pm3.append(_direction_check)
        pm3.append(_direction, condition=_direction_condition)
    pm3.append(_reset)
    pm3.append(_depth_check + _opt + _unroll, do_while=_opt_control)
    pm3.append(_scheduling)
    pm3.append(_alignments)
    pm3.append(_pulse_context)

    return pm3

