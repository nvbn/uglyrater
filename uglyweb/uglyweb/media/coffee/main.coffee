class Base
    authorised = false
    uid = 0

    check_auth: ->
        if @authorised
            return true
        else
            $.gritter.add {
            	title: 'Нененене!',
            	text: 'Это действие требует авторизации!'
            }
            return false

    template_name: ->
        if @authorised
            return '#logout_tpl'
        else
            return '#login_tpl'

    fill: (data) ->
        data = data['response'][0]
        @first_name = data.first_name
        @last_name = data.last_name
        @photo = data.photo
        @render()

    render: ->
        @obj = $(@template_name()).tmpl({
            base: this
        })
        $('#login_panel').html @obj

base = new Base()
conn = io.connect('http://localhost')

class RatesObj
    constructor: (rates) ->
        for rate in rates
            @set rate.uid, rate.value

    set: (uid, value) ->
        this[uid] = value

    get: (uid) ->
        this[uid]


class Profile
    constructor: (profile, @value) ->
        @first_name = profile.first_name
        @last_name = profile.last_name
        @photo = profile.photo
        @rate = profile.rate
        @uid = profile.uid
        @template_name = '#profile_tpl'

    render: ->
        minus_cls = 'rate rate_minus'
        plus_cls = 'rate rate_plus'
        if @value == 2
            plus_cls = plus_cls + ' active'
        else if @value == 1
            minus_cls = minus_cls + ' active'
        @obj = $(@template_name).tmpl {
            profile: this,
            minus_cls: minus_cls,
            plus_cls: plus_cls
        }
        @obj.find('a').click (event) ->
            event.preventDefault()
            if base.check_auth()
                conn.emit 'set_rate', $(this).parent().parent().attr('id'), $(this).hasClass 'rate_plus'
        @obj

    get: ->
        $('#' + @uid)


class TopObj
    constructor: (profiles, rates) ->
        @rates_obj = new RatesObj rates
        @profiles = (new Profile profile, @rates_obj.get(profile.uid) for profile in profiles)

    render: (to) ->
        @output = $(to)
        $(to).empty()
        for profile in @profiles
            $(to).append profile.render()


conn.on 'connect', () ->
    $('#loader').css 'display', 'none'
    $('#main').css 'display', 'block'
    conn.emit 'subscribe'
    conn.emit 'authorise', $.cookie('uid'), $.cookie('secret')
    $('#add').click (event) ->
        event.preventDefault()
        if base.check_auth()
            conn.emit 'add', $('#url').val()
            $('#url').val ''
            $('#url').attr 'placeholder', 'Готово!'

conn.on 'authorise_result', (status) ->
    base.authorised = status
    base.uid = $.cookie('uid')
    if base.uid
        VK.Api.call 'getProfiles', {
            uids: base.uid,
            fields: 'first_name, last_name, photo'
        }, (data) ->
            base.fill data
    else
        base.render()

conn.on 'update', (profiles, rates) ->
    top_object = new TopObj profiles, rates
    top_object.render '#list'
