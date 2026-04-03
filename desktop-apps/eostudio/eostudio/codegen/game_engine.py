"""Game engine export for EoStudio designs.

Supported targets: godot (.tscn + GDScript), unity (.prefab + C#),
unreal (C++ Actor classes).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


class GameEngineExporter:
    """Exports EoStudio game designs to engine-native formats."""

    SUPPORTED_TARGETS = ("godot", "unity", "unreal")

    def __init__(self, target: str = "godot") -> None:
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(f"Unknown target {target!r}")
        self._target = target

    def generate(self, screens: List[Dict[str, Any]],
                 app_name: str = "MyGame") -> Dict[str, str]:
        if not screens:
            screens = [{"name": "MainScene", "components": []}]
        dispatch = {"godot": self._gen_godot, "unity": self._gen_unity,
                    "unreal": self._gen_unreal}
        return dispatch[self._target](screens, app_name)

    # -- Godot --------------------------------------------------------

    def _gen_godot(self, screens: List[Dict[str, Any]],
                   app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        files["project.godot"] = (
            "[gd_resource type=\"Environment\" format=3]\n\n"
            "[application]\n\n"
            f'config/name="{app_name}"\n'
            'run/main_scene="res://scenes/Main.tscn"\n'
            'config/features=PackedStringArray("4.2")\n')

        for s in screens:
            name = self._pascal(s.get("name", "Main"))
            comps = s.get("components", [])
            nodes = self._godot_nodes(comps, name)
            files[f"scenes/{name}.tscn"] = (
                f'[gd_scene format=3]\n\n'
                f'[node name="{name}" type="Node2D"]\n'
                f'{nodes}')
            files[f"scripts/{name}.gd"] = (
                f'extends Node2D\n\n'
                f'func _ready():\n'
                f'    print("{name} scene loaded")\n\n'
                f'func _process(delta):\n'
                f'    pass\n')
        return files

    def _godot_nodes(self, components: List[Dict[str, Any]],
                     parent: str) -> str:
        lines: List[str] = []
        type_map = {"Button": "Button", "Text": "Label", "Input": "LineEdit",
                    "Image": "Sprite2D", "Container": "VBoxContainer",
                    "Card": "PanelContainer"}
        for i, c in enumerate(components):
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", f"Node{i}"))
            gt = type_map.get(ct, "Control")
            node_name = self._pascal(lb) or f"{gt}{i}"
            lines.append(f'\n[node name="{node_name}" type="{gt}" parent="."]\n')
            if ct == "Button":
                lines.append(f'text = "{lb}"\n')
            elif ct in ("Text", "Input"):
                lines.append(f'text = "{lb}"\n')
            if ct == "Container":
                for j, ch in enumerate(c.get("children", [])):
                    child_lines = self._godot_nodes([ch], node_name)
                    lines.append(child_lines)
        return "".join(lines)

    # -- Unity --------------------------------------------------------

    def _gen_unity(self, screens: List[Dict[str, Any]],
                   app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        for s in screens:
            name = self._pascal(s.get("name", "Main"))
            comps = s.get("components", [])
            body = self._unity_gameobjects(comps, 2)
            files[f"Assets/Scripts/{name}Controller.cs"] = (
                "using UnityEngine;\n"
                "using UnityEngine.UI;\n\n"
                f"public class {name}Controller : MonoBehaviour\n{{\n"
                f"    void Start()\n    {{\n"
                f"        Debug.Log(\"{name} loaded\");\n"
                f"{body}"
                f"    }}\n\n"
                f"    void Update()\n    {{\n    }}\n}}\n")
        files["Assets/Scripts/GameManager.cs"] = (
            "using UnityEngine;\n\n"
            f"public class GameManager : MonoBehaviour\n{{\n"
            f"    void Awake()\n    {{\n"
            f"        Debug.Log(\"{app_name} started\");\n"
            f"    }}\n}}\n")
        return files

    def _unity_gameobjects(self, components: List[Dict[str, Any]],
                           indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for i, c in enumerate(components):
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", f"Object{i}"))
            vname = f"obj{i}"
            if ct == "Button":
                lines.append(f'{pad}var {vname} = new GameObject("{lb}");\n')
                lines.append(f'{pad}{vname}.AddComponent<Button>();\n')
            elif ct == "Text":
                lines.append(f'{pad}var {vname} = new GameObject("{lb}");\n')
                lines.append(f'{pad}{vname}.AddComponent<Text>().text = "{lb}";\n')
            elif ct == "Image":
                lines.append(f'{pad}var {vname} = new GameObject("{lb}");\n')
                lines.append(f'{pad}{vname}.AddComponent<UnityEngine.UI.Image>();\n')
        return "".join(lines)

    # -- Unreal -------------------------------------------------------

    def _gen_unreal(self, screens: List[Dict[str, Any]],
                    app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        for s in screens:
            name = self._pascal(s.get("name", "Main"))
            comps = s.get("components", [])
            props = self._unreal_properties(comps, 1)
            files[f"Source/{name}Actor.h"] = (
                "#pragma once\n\n"
                "#include \"CoreMinimal.h\"\n"
                "#include \"GameFramework/Actor.h\"\n"
                f"#include \"{name}Actor.generated.h\"\n\n"
                f"UCLASS()\nclass A{name}Actor : public AActor\n{{\n"
                f"    GENERATED_BODY()\n\npublic:\n"
                f"    A{name}Actor();\n\nprotected:\n"
                f"    virtual void BeginPlay() override;\n\npublic:\n"
                f"    virtual void Tick(float DeltaTime) override;\n"
                f"{props}"
                f"}};\n")
            files[f"Source/{name}Actor.cpp"] = (
                f"#include \"{name}Actor.h\"\n\n"
                f"A{name}Actor::A{name}Actor()\n{{\n"
                f"    PrimaryActorTick.bCanEverTick = true;\n}}\n\n"
                f"void A{name}Actor::BeginPlay()\n{{\n"
                f"    Super::BeginPlay();\n"
                f"    UE_LOG(LogTemp, Log, TEXT(\"{name} Actor spawned\"));\n}}\n\n"
                f"void A{name}Actor::Tick(float DeltaTime)\n{{\n"
                f"    Super::Tick(DeltaTime);\n}}\n")

        files[f"Source/{self._pascal(app_name)}.Build.cs"] = (
            "using UnrealBuildTool;\n\n"
            f"public class {self._pascal(app_name)} : ModuleRules\n{{\n"
            f"    public {self._pascal(app_name)}(ReadOnlyTargetRules Target) : base(Target)\n    {{\n"
            "        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;\n"
            "        PublicDependencyModuleNames.AddRange(new string[] { \"Core\", \"CoreUObject\", \"Engine\", \"InputCore\" });\n"
            "    }\n}\n")
        return files

    def _unreal_properties(self, components: List[Dict[str, Any]],
                           indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for i, c in enumerate(components):
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", f"Prop{i}"))
            prop_name = self._pascal(lb) or f"Property{i}"
            if ct in ("Text", "Input"):
                lines.append(f"\n{pad}UPROPERTY(EditAnywhere)\n"
                             f"{pad}FString {prop_name} = TEXT(\"{lb}\");\n")
            elif ct == "Button":
                lines.append(f"\n{pad}UPROPERTY(EditAnywhere)\n"
                             f"{pad}bool b{prop_name}Pressed = false;\n")
        return "".join(lines)

    @staticmethod
    def _pascal(name: str) -> str:
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)
