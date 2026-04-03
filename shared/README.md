# 🔗 Shared Code

Reusable code shared across all EoS app categories. One fix here benefits every platform automatically.

## Structure

```
shared/
├── js/               # JavaScript/TypeScript utilities (browser, Node, Electron)
│   ├── auth.js       # Authentication helpers
│   ├── api.js        # API client
│   ├── storage.js    # Local/cloud storage abstraction
│   └── utils.js      # Common utilities
├── flutter/          # Dart packages shared by mobile apps
│   ├── eos_auth/     # Authentication package
│   ├── eos_ui/       # Common widgets & theme
│   └── eos_api/      # API client package
├── libs/             # C libraries shared by native/embedded apps
│   ├── eos_net.h     # Network abstraction
│   ├── eos_storage.h # Storage abstraction
│   └── eos_ui.h      # UI component library
└── python/           # Python packages shared by EoStudio
    ├── eos_formats/  # File format handlers
    └── eos_codegen/  # Code generation utilities
```

## Usage

### JavaScript (extensions, desktop Electron, web)
```js
import { authenticate } from '@eos/shared/auth';
import { apiClient } from '@eos/shared/api';
```

### Flutter (mobile apps)
```yaml
# pubspec.yaml
dependencies:
  eos_auth:
    path: ../../shared/flutter/eos_auth
```

### C (native apps, eBrowser)
```c
#include "shared/libs/eos_net.h"
#include "shared/libs/eos_storage.h"
```

### Python (EoStudio)
```python
from shared.python.eos_formats import load_project
```

## Principle

> Write once, use everywhere. Every platform imports from `shared/` so bug fixes and improvements propagate automatically.
