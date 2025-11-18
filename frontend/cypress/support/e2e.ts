// ***********************************************************
// This file is processed and loaded automatically before test files.
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Prevent TypeScript errors
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to select DOM element by data-testid attribute.
       * @example cy.getByTestId('greeting')
       */
      getByTestId(value: string): Chainable<JQuery<HTMLElement>>
    }
  }
}

export {}
