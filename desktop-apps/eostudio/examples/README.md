# EoStudio Example Projects

5 complete example projects demonstrating real EoStudio workflows.

## Projects

| Directory | Workflow | Difficulty |
|-----------|----------|------------|
| [todo-app](../examples/) | UI Designer → React/Flutter code → working app | Beginner |
| [mechanical-part](../examples/) | CAD Designer → OpenSCAD → 3D printable STL | Intermediate |
| [game-platformer](../examples/) | Game Editor → Godot/Unity export | Intermediate |
| [iot-dashboard](../examples/) | Database + UI Designer → Full-stack webapp | Advanced |
| [simulation-pid](../examples/) | Simulation Editor → PID controller analysis | Intermediate |

## Creating From Templates

```bash
# Create any example project
EoStudio new --template todo-app -o ./my-todo-app
EoStudio new --template mechanical-part -o ./my-bracket
EoStudio new --template game-platformer -o ./my-game
EoStudio new --template iot-dashboard -o ./my-dashboard
EoStudio new --template simulation-pid -o ./my-sim
```

## Workflow

1. **Create** a project from a template using `EoStudio new`
2. **Open** the `.eostudio` file in the appropriate editor
3. **Modify** the design using the visual editor
4. **Generate** code for your target framework
5. **Build** and run the generated project

See individual project READMEs for detailed walkthroughs.
