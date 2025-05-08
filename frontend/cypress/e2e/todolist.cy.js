describe('Todo list tests', () => {
  // define variables that we need on multiple occasions
  let uid // user id
  let email // email of the user
  const taskTitle = 'Learning Cypress'
  const youtubeKey = 'BQqzfHQkREo'
  const taskDescription = 'Watch the video to learn Cypress'

  before(function () {
    // Create user once before all tests
    cy.fixture('user.json')
      .then((user) => {
        cy.request({
          method: 'POST',
          url: 'http://localhost:5000/users/create',
          form: true,
          body: user
        }).then((response) => {
          uid = response.body._id.$oid
          email = user.email
        })
      })
  })

  beforeEach(() => {
    cy.viewport(1200, 1600);
    // Visit and log in before each test
    cy.visit('http://localhost:3000')
    cy.contains('div', 'Email Address').find('input[type=text]').type(email)
    cy.get('form').submit()

    // Create task (idempotent due to title check or server overwrite)
    cy.get('input[name="title"]').type(taskTitle)
    cy.get('input[name="url"]').type(youtubeKey)
    cy.get('input[type="submit"][value="Create new Task"]').click()

    // Visit task
    cy.contains(taskTitle).click()
  })

  it('does not allow creating todo with empty description', () => {
    // Ensure the input is empty
    cy.get('form.inline-form input[type="text"]').should('have.value', '')

    // Ensure the Add button is disabled
    cy.get('form.inline-form input[type="submit"]').should('be.disabled')

    // Count the current number of todo items (excluding the input form)
    cy.get('.todo-item')
      .then(($itemsBefore) => {
        const countBefore = $itemsBefore.length

        // Try to click the Add button even though it's disabled
        cy.get('form.inline-form input[type="submit"]').click({ force: true }) // force just to simulate the click attempt

        // Ensure the number of todo items remains unchanged
        cy.get('.todo-item').should('have.length', countBefore)
      })
  })

  it('allow creating todo with non-empty description and appends todo item to bottom', () => {
    // Count the current number of todo items
    cy.get('.todo-item')
      .then(($itemsBefore) => {
        const countBefore = $itemsBefore.length

        // Ensure the input is empty
        cy.get('form.inline-form input[type="text"]').type(taskDescription)

        // Ensure the Add button is disabled
        cy.get('form.inline-form input[type="submit"]').should('be.enabled').click()

        // Ensure the number of todo items increased by 1
        cy.get('.todo-item').should('have.length', countBefore + 1)

        // Assert that the last todo in the list matches the added description
        cy.get('.todo-item').last().should('contain.text', taskDescription)

        // Assert that the new todo item is not marked as done
        cy.get('.todo-item').last().within(() => {
          cy.get('.checker').should('not.have.class', 'checked') // not done
          cy.get('.editable')
            .should('exist')
            .and(($el) => {
              // Ensure it's not struck through (no line-through)
              expect($el).to.have.css('text-decoration-line', 'none')
            })
        })
      })
  })

  it('sets item to done and strikes through description when icon is clicked and todo item is initially active', () => {
    cy.get('.todo-item').last().within(() => {
      // Make sure it starts as active
      cy.get('.checker').should('not.have.class', 'checked')
      cy.get('.editable').should('have.css', 'text-decoration-line', 'none')
  
      // Click the checker
      cy.get('.checker').click()
  
      // Now it should be marked as done
      cy.get('.checker').should('have.class', 'checked')
      cy.get('.editable').should('have.css', 'text-decoration-line', 'line-through')
    })
  })

  it('sets item to active and removes strike through when icon is clicked and todo item is initially done', () => {
    cy.get('.todo-item').last().within(() => {
      // Precondition: ensure it is done
      cy.get('.checker').then(($checker) => {
        if (!$checker.hasClass('checked')) {
          cy.wrap($checker).click() // set it to done first
        }
      })
  
      cy.get('.checker').should('have.class', 'checked')
      cy.get('.editable').should('have.css', 'text-decoration-line', 'line-through')
  
      // Click again to toggle back to active
      cy.get('.checker').click()
  
      cy.get('.checker').should('not.have.class', 'checked')
      cy.get('.editable').should('have.css', 'text-decoration-line', 'none')
    })
  })

  it('deletes the todo item when the remover (x) symbol is clicked', () => {
    // Make sure the todo item exists
    cy.get('.todo-item').last().within(() => {
      cy.get('.editable').should('contain.text', 'Watch the video to learn Cypress')
    })
  
    // Count the current number of todo items
    cy.get('.todo-item').then(($itemsBefore) => {
      const countBefore = $itemsBefore.length
  
      // Click the remover symbol on the last todo
      cy.get('.todo-item').last().within(() => {
        cy.get('.remover').click()
      })
  
      // Ensure the number of todo items decreased by 1
      cy.get('.todo-item').should('have.length', countBefore - 1)
  
      // Ensure the deleted item is no longer present
      cy.get('.todo-item').each(($el) => {
        cy.wrap($el).should('not.contain.text', 'Watch the video to learn Cypress')
      })
    })
  })

  after(function () {
    // clean up by deleting the user from the database
    cy.request({
      method: 'DELETE',
      url: `http://localhost:5000/users/${uid}`
    }).then((response) => {
      cy.log(response.body)
      cy.visit('http://localhost:3000')
    })
  })
})