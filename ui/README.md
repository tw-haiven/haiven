# React UI [experimental]

Using the Boba PoC as a basis, we're working on a Javascript-based UI.

## How to run

Prerequisites:

- Node.JS 22
- Yarn

```
yarn install
yarn dev
```

--> localhost:3000/

API calls in "dev" mode will be rewritten to localhost:8080, the Python backend

## Publish to Haiven

Builds and then copies the static site to the folder from where it will be mounted into Haiven.

```
yarn copy
```
