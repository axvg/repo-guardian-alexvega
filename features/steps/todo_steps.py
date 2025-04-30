from behave import given, when, then


@given('una condicion simple')
def given_step(context):
    context.condition = True


@when('se hace algo')
def when_step(context):
    context.action = "completed"


@then('se obtiene un resultado exitoso')
def then_step(context):
    assert context.condition is True
