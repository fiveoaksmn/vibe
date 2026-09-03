### Vibe

Vibe lets you control the system’s vibe—through ambient messaging and customizable theming. Customize the look and feel of the interface to match the message, creating a cohesive experience that feels intentional, not noisy. Vibe keeps everyone aligned by combining communication and visual tone into a single, shared layer.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch deploy
bench install-app vibe
```

Optionally install the `rcssmin` library for minified CSS.

```angular2html
pip install rcssmin
```

### See Also

The color palette that Frappe uses can be found in `frappe/public/scss/espresso/_colors.scss`.

### License

mit
