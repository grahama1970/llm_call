JavaScript destructuring fails with Lucide's UMD build due to how the library structures its global export. When loaded via ``, Lucide creates a global `lucide` object containing **factory functions** rather than direct component exports[1][2]. 

The key technical reasons are:

1. **UMD Structure**: 
   - Lucide's UMD bundle exports an object with methods like `createIcons` and `icons` collection[3]
   - Individual icons exist as factory functions inside `lucide.icons` rather than direct properties[2]

2. **Destructuring Limitations**:
   ```js
   // Fails - tries to access nonexistent direct properties
   const { CheckCircle2 } = lucide; 

   // Works - accesses factory method through icons collection
   const CheckCircle2 = lucide.icons.CheckCircle2;
   ```

3. **React Component Requirements**:
   - Solid/React need component constructors, but UMD version provides:
   ```js
   lucide.icons.CheckCircle2 // → Function returning SVG element
   ```
   - ES Modules version provides:
   ```js
   import { CheckCircle2 } from 'lucide-react' // → React component
   ```

4. **Babel Standalone Interaction**:
   - UMD initialization timing affects availability
   - Direct assignment works through late-binding
   - Destructuring captures `undefined` at parse time

**Solution**: Use either:
```js
// Direct access
const CheckCircle2 = lucide.icons.CheckCircle2;

// Or initialize properly
lucide.createIcons();
const { CheckCircle2 } = lucide.icons; 
```

This behavior stems from UMD's compatibility layer prioritizing script-based initialization over ES module static analysis[1][3]. The ES module version (used in bundlers like Vite) enables proper destructuring through explicit named exports[3][2].

[1] https://unpkg.com/lucide@latest
[2] tools.data_visualization
[3] https://lucide.dev/icons/circle-check
[4] https://github.com/lucide-icons/lucide/issues/1675
[5] https://github.com/lucide-icons/lucide/issues/2834
[6] https://lucide.dev/guide/packages/lucide
[7] https://lucide.dev/guide/packages/lucide-static
[8] https://stackoverflow.com/questions/56054235/how-to-fix-the-white-screen-after-build-with-create-react-app
[9] https://www.jsdelivr.com/package/npm/lucide
[10] https://stackoverflow.com/questions/5257923/how-to-load-local-script-files-as-fallback-in-cases-where-cdn-are-blocked-unavai
[11] https://www.paigeniedringhaus.com/blog/use-es-6-to-destructure-deeply-nested-objects-in-javascript
[12] https://stackoverflow.com/questions/41137896/how-to-use-deep-destructuring-on-imports-in-es6-syntax