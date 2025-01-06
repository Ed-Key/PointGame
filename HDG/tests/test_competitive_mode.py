# tests/test_competitive_mode.py
import pytest
from HDG.game.managers import CompetitiveGameManager
from HDG.game.managers.event_manager import GameEvent

class TestCompetitiveMode:
    @pytest.fixture
    def game_manager(self):
        return CompetitiveGameManager()
    
    def test_multiple_players(self, game_manager):
        # Add multiple players
        player_ids = [
            game_manager.add_player(f"Player {i}")
            for i in range(5)
        ]
        
        # Verify turn rotation
        first_rotation = [game_manager.next_turn() for _ in range(5)]
        assert first_rotation == player_ids
        
        # Verify wrapping
        assert game_manager.next_turn() == player_ids[0]
    
    def test_player_state_updates(self, game_manager):
        player_id = game_manager.add_player("Test Player")
        game_manager.update_player_score(player_id, 100)
        
        player_state = game_manager.players[player_id]
        assert player_state.score == 100
    
    def test_event_emission(self, game_manager):
        events_received = []
        
        def on_turn_changed(player_id, name):
            events_received.append(("turn_changed", player_id))
        
        game_manager.event_manager.subscribe(GameEvent.TURN_CHANGED, on_turn_changed)
        
        player_id = game_manager.add_player("Test Player")
        game_manager.next_turn()
        
        assert len(events_received) == 1
        assert events_received[0][0] == "turn_changed"
        assert events_received[0][1] == player_id