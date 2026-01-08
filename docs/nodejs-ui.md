# Node.js Style UI for Nami Code Assistant

This feature adds a Node.js-inspired styling to the Nami Code Assistant CLI, providing a familiar interface for Node.js developers.

## Features

- **Node.js Green Color Scheme**: Uses the iconic Node.js green (#339933) as the primary color
- **Custom ASCII Art**: Node.js styled banner
- **Enhanced Prompt**: Custom prompt styling with Node.js aesthetics
- **Themed Components**: File operations, todo lists, and other UI elements styled to match Node.js conventions

## Usage

To use the Node.js style UI, simply add the `--nodejs-style` flag when starting the CLI:

```bash
nami --nodejs-style
```

Or with other options:

```bash
nami --nodejs-style --agent my-agent
nami --nodejs-style --auto-approve
```

## Customization

The Node.js style UI can be further customized by modifying the following files:

- `namicode_cli/nodejs_ui_config.py`: Color scheme and ASCII art
- `namicode_cli/nodejs_ui_components.py`: UI components and rendering
- `namicode_cli/nodejs_prompt.py`: Prompt session styling
- `namicode_cli/nodejs_ui.py`: Integration points

## Screenshots

![Node.js Style UI](assets/nodejs-ui-example.png)

*Example of the Node.js style UI in action*

## Contributing

Feel free to customize the Node.js style UI further by:

1. Modifying the color scheme in `nodejs_ui_config.py`
2. Adding new UI components in `nodejs_ui_components.py`
3. Enhancing the prompt experience in `nodejs_prompt.py`

## License

This Node.js style UI is part of the Nami Code Assistant project and follows the same license terms.