describe('Adding todo item', () => {
  // define variables that we need on multiple occasions
  let uid // user id
  let name // name of the user (firstName + ' ' + lastName)
  let email // email of the user

  before(function () {
    cy.fixture('user.json')
      .then((user) => {
        cy.request({
          method: 'POST',
          url: 'http://localhost:5000/users/create',
          form: true,
          body: user
        }).then((response) => {
          uid = response.body._id.$oid
          name = user.firstName + ' ' + user.lastName
          email = user.email

          // Log in only once
          cy.visit('http://localhost:3000')
          cy.contains('div', 'Email Address')
            .find('input[type=text]')
            .type(email)
          cy.get('form').submit()
          cy.get('h1').should('contain.text', 'Your tasks, ' + name)
        })
      })
  })

  it('creating a new task', () => {
    
  })

  after(function () {
    // clean up by deleting the user from the database
    cy.request({
      method: 'DELETE',
      url: `http://localhost:5000/users/${uid}`
    }).then((response) => {
      cy.log(response.body)
    })
  })
})