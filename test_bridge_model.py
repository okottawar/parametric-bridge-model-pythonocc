"""
Test Script for Bridge Model
Tests various configurations and validates geometry creation
"""

import sys
import os

# Test different bridge configurations
test_configurations = [
    {
        "name": "Default Configuration",
        "span_length": 12000,
        "n_girders": 3,
        "spacing": 3000,
        "overhang": 500,
        "skew_angle": 10,
        "girder_d": 900,
        "girder_bf": 300,
        "girder_tf": 16,
        "girder_tw": 10,
        "deck_thickness": 200,
    },
    {
        "name": "4-Girder Bridge",
        "span_length": 15000,
        "n_girders": 4,
        "spacing": 2500,
        "overhang": 500,
        "skew_angle": 0,
        "girder_d": 1000,
        "girder_bf": 350,
        "girder_tf": 20,
        "girder_tw": 12,
        "deck_thickness": 250,
    },
    {
        "name": "Wide Bridge with Skew",
        "span_length": 20000,
        "n_girders": 5,
        "spacing": 3500,
        "overhang": 600,
        "skew_angle": 15,
        "girder_d": 1200,
        "girder_bf": 400,
        "girder_tf": 25,
        "girder_tw": 15,
        "deck_thickness": 300,
    },
]


def test_component_creation():
    """Test individual component creation."""
    print("\n" + "=" * 70)
    print("TEST 1: Component Creation")
    print("=" * 70)
    
    try:
        from bridge_model import Girder, Deck, Parapet
        
        # Test Girder
        print("\nTesting Girder creation...")
        girder = Girder(d=900, bf=300, tf=16, tw=10, length=12000)
        girder.create_geometry()
        assert girder.get_shape() is not None, "Girder shape is None"
        print("  ✓ Girder created successfully")
        
        # Test Deck
        print("\nTesting Deck creation...")
        deck = Deck(width=7000, thickness=200, length=12000)
        deck.create_geometry()
        assert deck.get_shape() is not None, "Deck shape is None"
        print("  ✓ Deck created successfully")
        
        # Test Parapet
        print("\nTesting Parapet creation...")
        parapet = Parapet(width=300, height=1000, length=12000)
        parapet.create_geometry()
        assert parapet.get_shape() is not None, "Parapet shape is None"
        print("  ✓ Parapet created successfully")
        
        print("\n✓ All component creation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Component creation test failed: {e}")
        return False


def test_transformations():
    """Test component transformations."""
    print("\n" + "=" * 70)
    print("TEST 2: Component Transformations")
    print("=" * 70)
    
    try:
        from bridge_model import Girder
        from OCC.Core.gp import gp_Pnt, gp_Dir
        
        # Create a test girder
        print("\nTesting translation...")
        girder = Girder(d=900, bf=300, tf=16, tw=10, length=12000)
        girder.create_geometry()
        
        # Test translation
        girder.translate(100, 200, 300)
        print("  ✓ Translation successful")
        
        # Test rotation
        print("\nTesting rotation...")
        girder2 = Girder(d=900, bf=300, tf=16, tw=10, length=12000)
        girder2.create_geometry()
        girder2.rotate(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), 45)
        print("  ✓ Rotation successful")
        
        print("\n✓ All transformation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Transformation test failed: {e}")
        return False


def test_bridge_configurations():
    """Test various bridge configurations."""
    print("\n" + "=" * 70)
    print("TEST 3: Bridge Configurations")
    print("=" * 70)
    
    from bridge_model import BridgeModel
    
    all_passed = True
    
    for config in test_configurations:
        print(f"\nTesting: {config['name']}")
        print("-" * 70)
        
        try:
            bridge = BridgeModel(
                span_length=config['span_length'],
                n_girders=config['n_girders'],
                spacing=config['spacing'],
                overhang=config['overhang'],
                skew_angle=config['skew_angle'],
                girder_section_d=config['girder_d'],
                girder_section_bf=config['girder_bf'],
                girder_section_tf=config['girder_tf'],
                girder_section_tw=config['girder_tw'],
                deck_thickness=config['deck_thickness']
            )
            
            # Test layout computation
            bridge.compute_layout()
            assert bridge.deck_width is not None, "Deck width not computed"
            assert len(bridge.girder_positions_y) == config['n_girders'], \
                f"Expected {config['n_girders']} girder positions"
            print(f"  ✓ Layout computed: Deck width = {bridge.deck_width} mm")
            
            # Test component creation
            bridge.create_components()
            assert len(bridge.girders) == config['n_girders'], \
                f"Expected {config['n_girders']} girders"
            assert bridge.deck is not None, "Deck not created"
            assert len(bridge.parapets) == 2, "Expected 2 parapets"
            print(f"  ✓ Components created: {len(bridge.girders)} girders, 1 deck, 2 parapets")
            
            # Test positioning
            bridge.position_components()
            print(f"  ✓ Components positioned")
            
            # Test assembly
            bridge.assemble()
            assert bridge.assembly_shape is not None, "Assembly shape is None"
            print(f"  ✓ Assembly created")
            
            print(f"\n  ✓ {config['name']} test passed!")
            
        except Exception as e:
            print(f"\n  ✗ {config['name']} test failed: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All bridge configuration tests passed!")
    else:
        print("\n✗ Some bridge configuration tests failed")
    
    return all_passed


def test_parameter_validation():
    """Test parameter validation and edge cases."""
    print("\n" + "=" * 70)
    print("TEST 4: Parameter Validation")
    print("=" * 70)
    
    from bridge_model import BridgeModel
    
    test_cases = [
        {
            "name": "Minimum girders (3)",
            "n_girders": 3,
            "should_pass": True
        },
        {
            "name": "Many girders (6)",
            "n_girders": 6,
            "should_pass": True
        },
        {
            "name": "Zero skew angle",
            "skew_angle": 0,
            "should_pass": True
        },
        {
            "name": "Maximum skew angle (15°)",
            "skew_angle": 15,
            "should_pass": True
        },
    ]
    
    all_passed = True
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        
        try:
            kwargs = {
                'span_length': 12000,
                'n_girders': test.get('n_girders', 3),
                'spacing': 3000,
                'overhang': 500,
                'skew_angle': test.get('skew_angle', 10),
                'girder_section_d': 900,
                'girder_section_bf': 300,
                'girder_section_tf': 16,
                'girder_section_tw': 10,
                'deck_thickness': 200
            }
            
            bridge = BridgeModel(**kwargs)
            bridge.compute_layout()
            bridge.create_components()
            
            if test['should_pass']:
                print(f"  ✓ Test passed as expected")
            else:
                print(f"  ✗ Test should have failed but passed")
                all_passed = False
                
        except Exception as e:
            if not test['should_pass']:
                print(f"  ✓ Test failed as expected: {e}")
            else:
                print(f"  ✗ Test failed unexpectedly: {e}")
                all_passed = False
    
    if all_passed:
        print("\n✓ All parameter validation tests passed!")
    else:
        print("\n✗ Some parameter validation tests failed")
    
    return all_passed


def run_all_tests():
    """Run all test suites."""
    print("=" * 70)
    print("BRIDGE MODEL TEST SUITE")
    print("=" * 70)
    
    results = {
        "Component Creation": test_component_creation(),
        "Transformations": test_transformations(),
        "Bridge Configurations": test_bridge_configurations(),
        "Parameter Validation": test_parameter_validation(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED! ✓")
    else:
        print("SOME TESTS FAILED! ✗")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    # Make sure we can import bridge_model
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
