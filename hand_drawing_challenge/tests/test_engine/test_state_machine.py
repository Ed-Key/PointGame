import pytest
from hand_drawing_challenge.engine.state_machine import GameStateMachine, GameState, State

class MockState(State):
    """Mock state implementation for testing."""
    def __init__(self):
        super().__init__()
        self.entered = False
        self.exited = False
        self.updated = False
        self.last_delta = 0.0
    
    def enter(self) -> None:
        self.entered = True
    
    def exit(self) -> None:
        self.exited = True
    
    def update(self, delta_time: float) -> None:
        self.updated = True
        self.last_delta = delta_time

@pytest.fixture
def state_machine():
    """Create a fresh state machine for each test."""
    return GameStateMachine()

@pytest.fixture
def mock_states():
    """Create mock states for testing."""
    return {
        GameState.MENU: MockState(),
        GameState.PLAYING: MockState(),
        GameState.PAUSED: MockState()
    }

def test_initial_state(state_machine):
    """Test initial state is None."""
    assert state_machine.current_state is None
    assert state_machine.previous_state is None

def test_add_state(state_machine, mock_states):
    """Test adding states to the machine."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    assert GameState.MENU in state_machine.states
    assert state_machine.states[GameState.MENU].state_machine == state_machine

def test_change_state(state_machine, mock_states):
    """Test state transition mechanics."""
    # Add states
    menu_state = mock_states[GameState.MENU]
    playing_state = mock_states[GameState.PLAYING]
    state_machine.add_state(GameState.MENU, menu_state)
    state_machine.add_state(GameState.PLAYING, playing_state)
    
    # Change to MENU
    state_machine.change_state(GameState.MENU)
    assert state_machine.current_state == menu_state
    assert menu_state.entered
    assert not menu_state.exited
    
    # Change to PLAYING
    state_machine.change_state(GameState.PLAYING)
    assert state_machine.current_state == playing_state
    assert state_machine.previous_state == menu_state
    assert menu_state.exited
    assert playing_state.entered

def test_invalid_state_change(state_machine, mock_states):
    """Test handling of invalid state transitions."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    state_machine.change_state(GameState.MENU)
    
    # Try changing to non-existent state
    initial_state = state_machine.current_state
    state_machine.change_state(GameState.PLAYING)  # PLAYING not added
    assert state_machine.current_state == initial_state  # Should remain unchanged

def test_update_state(state_machine, mock_states):
    """Test state updates."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    state_machine.change_state(GameState.MENU)
    
    delta_time = 0.016  # Simulate 16ms frame time
    state_machine.update(delta_time)
    
    current_state = mock_states[GameState.MENU]
    assert current_state.updated
    assert current_state.last_delta == delta_time

def test_update_without_state(state_machine):
    """Test update behavior with no current state."""
    state_machine.update(0.016)  # Should not raise any errors
