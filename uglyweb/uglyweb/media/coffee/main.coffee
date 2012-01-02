class Base
    authorised = false

base = new Base
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
        if @value
            plus_cls = plus_cls + ' active'
        else
            minus_cls = minus_cls + ' active'
        result_obj = $(@template_name).tmpl {
            profile: this,
            minus_cls: minus_cls,
            plus_cls: plus_cls
        }
        result_obj.find('a').click (event) ->
            event.preventDefault()
            conn.emit 'set_rate', $(this).parent().attr('id'), $(this).hasClass 'rate_plus'
        result_obj

    get: ->
         $('#' + uid)


class TopObj
    constructor: (profiles, rates) ->
        @rates_obj = new RatesObj rates
        @profiles = (new Profile profile, @rates_obj.get(profile.uid) for profile in profiles)

    render: (to) ->
        $(to).empty()
        for profile in @profiles
            $(to).append profile.render()


conn.on 'connect', () ->
    conn.emit 'is_authorised', (status) ->
        base.authorised = status
    $('#add').click (event) ->
        event.preventDefault()
        conn.emit 'add', $('#url').val()


conn.on 'update', (profiles, rates) ->
    top_object = new TopObj(profiles, rates)
    top_object.render '#list'

